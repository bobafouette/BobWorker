import socket
import threading
import errno
import json

from worker import Worker
from model import Job

class Listener(threading.Thread):


    def __init__(self, port, node):
        super(Listener, self).__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket.gethostbyname('localhost'), port))
        self.node = node

    
    def run(self):
        while True:
            self.socket.listen(5)
            client, address = self.socket.accept()
            message = client.recv(255)

            message = message.split(' ')
            header = message[0]

            if header == 'JOB':
                print('catch Job')
                job = Job.readDesc(' '.join(message[1:]))
                self.node.pushJob(job)
            elif header == 'NODE':
                node = Node.readDesc(' '.join(message[1:]))
                self.node.replaceNeighbor(node, *address)
            
            client.send('ACK')
            client.close()

        self.socket.close()
        

class Node(object):


    @staticmethod
    def writeDesc(node):
        desc = {
            'port': node.port,
            'ip': node.ip,
        }
        return json.dumps(desc)


    @staticmethod
    def readDesc(desc):

        desc = json.loads(desc)
        node = Node(desc['port'], desc['ip'])
        return node


    def __init__(self, port, ip):

        print("INIT {ip}:{port}".format(ip= ip, port= port))
        self.worker = Worker()
        self.neighbors = []
        self.ip = ip
        self.port = port
        self.listener = Listener(port, self)
        self.listener.start()
        self.passedJobCounter = 0

    
    def addNeighbor(self, neighbor):

        if len(self.neighbors) >= 2:

            node = Node.writeDesc(neighbor)
            for index, currentNeighbor in enumerate(self.neighbors):

                socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_client.connect(((currentNeighbor.ip, currentNeighbor.port)))
                socket_client.send('NODE {node}'.format(node=node))
                response = socket_client.recv(255)
                socket_client.close()
                if response == 'ACK':
                    self.neighbors.pop(index)
                    break
                print('HOST {ip}:{port} did not answered properly: {response}'.format(ip=currentNeighbor.ip, port=currentNeighbor.port, response=response))
            else:
                raise ValueError('ERROR on all neighbors.')

        self.neighbors.append(neighbor)

    
    def replaceNeighbor(self, neighbor, originAddress, originPort):

        for index, currentNeighbor in enumerate(self.neighbors):
            if currentNeighbor.port != originPort or currentNeighbor.address != originAddress:
                continue

            self.neighbors.pop(index)
            break
        
        else:
            raise ValueError('No Node known with address {address} and port {port}'.format(
                originAddress,
                originPort
            ))

        self.addNeighbor(neighbor)
        
    

    def pushJob(self, job):

        job = self.worker.addJob(job)
        if not job:
            self.passedJobCounter = 0
            return
        
        if self.passedJobCounter > 5:
            self.passedJobCounter = 0
            self.startNode()

        self.passJob(job)

    def passJob(self, job):
        
        print('passJob')
        self.passedJobCounter += 1
        job = Job.writeDesc(job)
        for neighbor in self.neighbors:

            socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_client.connect(((neighbor.ip, neighbor.port)))
            socket_client.send('JOB {job}'.format(job=job))
            response = socket_client.recv(255)
            socket_client.close()
            if response == 'ACK':
                break
            print('Node {ip}:{port} did not answered properly: {response}'.format(ip=neighbor.ip, port=neighbor.port, response=response))
        else:
            raise ValueError('ERROR on all neighbors.')


    def startNode(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        selectedPort = -1

        currentPort = self.port
        while selectedPort == -1 and currentPort < 65535:
            try:
                s.bind(("127.0.0.1", currentPort))
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    continue
                raise e

        if selectedPort == -1:
            raise ValueError('All ports seems occupied.')

        newNode = Node(selectedPort, currentPort)
        self.addNeighbor(newNode)

        s.close()



if __name__ == '__main__':

    import argparse
    argParser = argparse.ArgumentParser(description= 'A P2P commands distributor.')
    argParser.add_argument('port', type= int,  help= 'A port to run the program on')
    argParser.add_argument('name', help= 'Name this node')
    
    args = argParser.parse_args()

    # tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # tcpsock.bind(("",args.port))

    # worker = Worker()

    # while True:
    #     tcpsock.listen(10)
    #     (clientsocket, (ip, port)) = tcpsock.accept()
    #     newthread = Node(ip, port, clientsocket, worker)
    #     newthread.start()
