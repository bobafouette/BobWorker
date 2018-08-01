import socket

from worker import Worker
from node import Node
from model import Job


port1 = 1111
port2 = 1112

node1 = Node(port1, '127.0.0.1')
node2 = Node(port2, '127.0.0.1')

node1.addNeighbor(node2)
node2.addNeighbor(node1)

job1 = Job('job1', {'name': 'job1'})
job1.addCommands(['echo "start: {name}"', 'sleep 100', 'echo "end: {name}"'])

job2 = Job('job2', {'name': 'job2'})
job2.addCommands(['echo "start: {name}"', 'sleep 100', 'echo "end: {name}"'])

job3 = Job('job3', {'name': 'job3'})
job3.addCommands(['echo "run {name}"'])

node1.pushJob(job1)
node1.pushJob(job2)
node1.pushJob(job3)

# WIP: auto node start

# The Worker has been reimplemented to be individual instead of shared between nodes.
# I try to implements a fonctionnality to allow a node to start another one when needed but still WIP:
