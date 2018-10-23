import socket
import threading
import signal

import netifaces as ni
from worker import Worker
from node import Node
from node import Neighbour
from model import Job


def getIpOf(interface):
    ni.ifaddresses(interface)
    ip = ni.ifaddresses(interface)[ni.AF_INET][0]["addr"]
    print(ip)
    return ip


def setupNode(wifi):
    LOCALIP = getIpOf(wifi)
    port = 1111
    return Node(LOCALIP, port)


def connect0To1(node, ipNode1, portNode1):
    neighbour = Neighbour(ipNode1, portNode1)
    node.connectTo(neighbour)


def addJobs(node):

    for index in range(3):
        jobName = "job{0}".format(index)
        job = Job(jobName, {"name": jobName})
        job.addCommands(['echo "start: {name}"', "sleep 10", 'echo "end: {name}"'])
        node.pushJob(job)


if __name__ == "__main__":
    import argparse
    import time

    argparser = argparse.ArgumentParser(description="Test the BobWorker Programm")
    argparser.add_argument(
        "nodeNumber", choices=[0, 1], type=int, help="The Node number"
    )
    argparser.add_argument("ip", help="The Neighbour ip address")
    argparser.add_argument("port", type=int, help="The Neighbour port number")
    argparser.add_argument("-i", "--interface", help="Network interface to use")
    args = argparser.parse_args()

    nodeNum = args.nodeNumber
    if nodeNum == 0:
        # Setup the first Node
        node = setupNode(args.interface)
        time.sleep(5)
        connect0To1(node, args.ip, args.port)
    elif nodeNum == 1:
        # Setup the second Node
        node = setupNode(args.interface)
        time.sleep(10)
        addJobs(node)
    else:
        raise ValueError("Unrecognized node number: {0}".format(nodeNum))
