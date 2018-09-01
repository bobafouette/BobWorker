import socket
import threading
import errno
import json
import logging
import sys
import time

from worker import Worker
from model import Job


class SignalHandler:
    """
    The object that will handle signals and stop the worker threads.
    """

    #: The stop event that's shared by this handler and threads.
    stopper = None

    #: The pool of worker threads
    workers = None

    def __init__(self, stopper):
        self.stopper = stopper

    def __call__(self, signum, frame):
        """
        This will be called by the python signal module

        https://docs.python.org/3/library/signal.html#signal.signal
        """

        self.stopper.set()
        sys.exit(0)


class Listener(threading.Thread):

    def __init__(self, port, node):
        super(Listener, self).__init__()
        self.node = node
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.node.ip, port))

    def run(self):
        while True:
            self.socket.listen(5)
            client, address = self.socket.accept()
            message = client.recv(255)

            message = message.split(' ')
            header = message[0]

            if header == 'JOB':
                job = Job.readDesc(' '.join(message[1:]))
                self.node.pushJob(job)

            elif header == 'NEIGHBOR':
                neighbor = Neighbor.readDesc(' '.join(message[1:]))
                self.node.addNeighbor(neighbor)
            client.close()

        self.node.exit()
        self.socket.close()


class Neighbor(object):

    @staticmethod
    def writeDesc(Neighbor):
        desc = {
            'port': Neighbor.port,
            'ip': Neighbor.ip,
        }
        return json.dumps(desc)

    @staticmethod
    def readDesc(desc):

        desc = json.loads(desc)
        neighbor = Neighbor(desc['port'], desc['ip'])
        return neighbor

    def __init__(self, ip, port):

        self.ip = ip
        self.port = port

    def passJob(self, job):

        job = Job.writeDesc(job)
        socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_client.connect(((self.ip, self.port)))
        socket_client.send('JOB {job}'.format(job=job))
        socket_client.close()

    def passNeighbor(self, neighbor):

        neighbor = neighbor.writeDesc(neighbor)
        socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_client.connect(((self.ip, self.port)))
        socket_client.send('NEIGHBOR {neighbor}'.format(neighbor=neighbor))
        socket_client.close()


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
        print('NewNode %s %s' % (ip, port))
        self.worker = Worker()
        self.neighbor = None
        self.ip = ip
        self.port = port
        self.listener = Listener(port, self)
        self.listener.start()
        self.passedJobCounter = 0

    def castHasNeighbor(self):
        return Neighbor(self.ip, self.port)

    def addNeighbor(self, neighbor):

        if self.neighbor:
            neighbor.passNeighbor(self.neighbor)
        self.neighbor = neighbor

    def pushJob(self, job):

        job = self.worker.addJob(job)
        if not job:
            self.passedJobCounter = 0
            return

        if self.passedJobCounter > 5:
            self.passedJobCounter = 0
            self.startNode()

        self.passedJobCounter += 1
        self.neighbor.passJob(job)

    def startNode(self):

        selectedPort = -1
        currentPort = self.port
        print('Selecting a port')

        while selectedPort == -1 and currentPort < 65535:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            currentPort += 1

            try:
                s.bind((self.ip, currentPort))
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    continue
                raise e

            s.close()
            selectedPort = currentPort

        if selectedPort == -1:
            raise ValueError('All ports seems occupied.')

        newNode = Node(selectedPort, self.ip).castHasNeighbor()
        print('Node initialized')
        self.addNeighbor(newNode)

    def exit(self):
        self.worker.exit()


if __name__ == '__main__':

    import argparse
    argParser = argparse.ArgumentParser(
        description='A P2P commands distributor.')
    argParser.add_argument(
        'port', type=int,  help='A port to run the program on')
    argParser.add_argument('name', help='Name this node')

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
