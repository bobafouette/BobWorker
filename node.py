import socket
import threading
import errno
import json
import sys
import time
import logging


from worker import Worker
from model import Job

# NOTE:Setup logger with a StreamHandler by default
logging.basicConfig()


class Listener(threading.Thread):
    def __init__(self, port, node):
        super(Listener, self).__init__()
        self.node = node
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.node.ip, port))
        logging.getLogger(self.__class__.__name__).setLevel(logging.INFO)

    def run(self):
        while True:
            self.socket.listen(5)
            client, address = self.socket.accept()
            message = client.recv(255).decode().split(" ")
            header = message[0]

            # Received a new job
            if header == Job.PROTOCOL_FLAG:
                logging.getLogger(self.__class__.__name__).info(
                    "Recieved a new Job: {0}".format(message)
                )
                job = Job.readDesc(" ".join(message[1:]))
                self.node.pushJob(job)

            # Received a new Neighbour
            elif header == Neighbour.PROTOCOL_FLAG:
                neighbour = Neighbour.readDesc(" ".join(message[1:]))
                logging.getLogger(self.__class__.__name__).info(
                    "Recieved a new Neighbour: {0}".format(message)
                )
                self.node.addNeighbour(neighbour)

            else:
                logging.getLogger(self.__class__.__name__).error(
                    "Message could not be interepreted: {0}".format(message)
                )

            client.close()

        self.node.exit()
        self.socket.close()


class Neighbour(object):

    PROTOCOL_FLAG = "NEIGHBOUR"

    @staticmethod
    def readDesc(desc):
        desc = json.loads(desc)
        neighbour = Neighbour(desc["ip"], desc["port"])
        return neighbour

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        logging.getLogger(self.__class__.__name__).setLevel(logging.INFO)

    def passObject(self, object_):
        object_Desc = object_.writeDesc()
        message = "{flag} {object_}".format(
            flag=object_.PROTOCOL_FLAG, object_=object_Desc
        ).encode()

        socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_client.connect(((self.ip, self.port)))
        socket_client.send(message)
        socket_client.close()

        logging.getLogger(self.__class__.__name__).info(
            "Pass an object: {0}".format(message)
        )

    def writeDesc(self):
        desc = {"port": self.port, "ip": self.ip}
        return json.dumps(desc)


class Node(object):

    PROTOCOL_FLAG = "NODE"

    @staticmethod
    def readDesc(desc):

        desc = json.loads(desc)
        node = Node(desc["port"], desc["ip"])
        return node

    def __init__(self, ip, port):
        self.worker = Worker()
        self.neighbour = None
        self.ip = ip
        self.port = port
        self.listener = Listener(port, self)
        self.listener.start()
        logging.getLogger(self.__class__.__name__).setLevel(logging.INFO)

    def castHasNeighbour(self):
        return Neighbour(self.ip, self.port)

    def addNeighbour(self, neighbour):

        if self.neighbour:
            neighbour.passObject(self.neighbour)
        self.neighbour = neighbour

    def pushJob(self, job):

        workerJob = self.worker.addJob(job)
        if job != workerJob:
            # The worker has returned an old Job, the new one is starting
            logging.getLogger(self.__class__.__name__).info("New Job started")
            return
        # The worker has return the new job. We have to pass it
        logging.getLogger(self.__class__.__name__).warning("Worker is busy pass Job")

        if self.neighbour:
            self.neighbour.passObject(job)
        else:
            # TODO: Lost, really??
            logging.getLogger(self.__class__.__name__).warning(
                "No neighbour to pass the Job. The Job is lost."
            )

    def connectTo(self, neighbour):
        self.neighbour = neighbour
        self.neighbour.passObject(self.castHasNeighbour())

    def startNode(self):

        selectedPort = -1
        currentPort = self.port

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
            raise ValueError("All ports seems occupied.")

        newNode = Node(self.ip, selectedPort).castHasNeighbour()
        self.addNeighbour(newNode)

    def writeDesc(self):
        desc = {"port": self.port, "ip": self.ip}
        return json.dumps(desc)


if __name__ == "__main__":

    import argparse

    argParser = argparse.ArgumentParser(description="A P2P commands distributor.")
    argParser.add_argument("port", type=int, help="A port to run the program on")
    argParser.add_argument("name", help="Name this node")

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
