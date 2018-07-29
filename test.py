import socket

from worker import Worker
from node import Node
from model import Job

worker1 = Worker()
worker2 = Worker()


port1 = 1111
port2 = 1112

node1 = Node(worker1, port1, '127.0.0.1')
node2 = Node(worker2, port2, '127.0.0.1')

node1.addNeighbours(node2)
node2.addNeighbours(node1)

job1 = Job('job1', {'name': 'job1'})
job1.addCommands(['echo "start: {name}"', 'sleep 10', 'echo "end: {name}"'])

job2 = Job('job2', {'name': 'job2'})
job2.addCommands(['echo "run {name}"'])

node1.pushJob(job1)
node1.pushJob(job2)
