import socket
import threading

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
                job = Job.read_desc(' '.join(message[1:]))
                self.node.pushJob(job)
            
            client.send('ACK')
            client.close()
        self.socket.close()
        

class Node(object):

    def __init__(self, worker, port, ip):

        self.worker = worker
        self.neighbours = []
        self.ip = ip
        self.port = port
        self.listener = Listener(port, self)
        self.listener.start()

    
    def addNeighbours(self, neighbours):

        if not isinstance(neighbours, list):
            neighbours = [neighbours]
        self.neighbours.extend(neighbours)
    

    def pushJob(self, job):
        job = self.worker.addJob(job)
        if not job:
            return
        self.passJob(job)

    def passJob(self, job):

        job = Job.write_desc(job)
        for neighbour in self.neighbours:

            socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_client.connect(((neighbour.ip, neighbour.port)))
            socket_client.send('JOB {job}'.format(job=job))
            response = socket_client.recv(255)
            socket_client.close()
            if response == 'ACK':
                break
            print('HOST {ip}:{port} did not answered properly: {response}'.format(ip=neighbour.ip, port=neighbour.port, response=response))
        else:
            raise ValueError('ERROR on all neighbours. ')



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
