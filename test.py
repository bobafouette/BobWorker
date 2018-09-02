import socket
import threading
import signal

import netifaces as ni
from worker import Worker
from node import Node
from node import Neighbor
from node import SignalHandler
from model import Job

WIFIINTERFACE = 'en0'


def getIpOf(interface):
    ni.ifaddresses(interface)
    ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
    return ip


LOCALIP = getIpOf(WIFIINTERFACE)

port1 = 1111
port2 = 1112

# stopper = threading.Event()
# handler = SignalHandler(stopper)
# signal.signal(signal.SIGINT, handler)

node1 = Node(LOCALIP, port1)
node2 = Node(LOCALIP, port2)

neighbour1 = Neighbor(LOCALIP, port1)
neighbour2 = Neighbor(LOCALIP, port2)

node1.addNeighbor(neighbour2)
node2.addNeighbor(neighbour1)

job1 = Job('job1', {'name': 'job1'})
job1.addCommands(['echo "start: {name}"', 'sleep 100', 'echo "end: {name}"'])

job2 = Job('job2', {'name': 'job2'})
job2.addCommands(['echo "start: {name}"', 'sleep 100', 'echo "end: {name}"'])

job3 = Job('job3', {'name': 'job3'})
job3.addCommands(['echo "run {name}"'])

node1.pushJob(job1)
node1.pushJob(job2)
node1.pushJob(job3)
