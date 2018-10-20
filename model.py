import subprocess
import json


class Job(object):

    @staticmethod
    def readDesc(desc):

        desc = json.loads(desc)
        job = Job(desc['name'], desc['metadata'])
        job.addCommands([' '.join(command) for command in desc['commands']])
        return job

    def __init__(self, name, metadata={}):
        self._name = name
        self.commands = []
        if not metadata:
            metadata = {}
        self.metadata = metadata

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def writeDesc(self):
        desc = {
            'commands': [list(command.split(' ')) for command in self.commands],
            'name': self.name,
            'metadata': self.metadata
        }
        return json.dumps(desc)

    def addCommands(self, commands):
        if not isinstance(commands, list):
            commands = [commands]
        self.commands.extend(commands)

    def execute(self):
        self.commands = [command.format(**self.metadata)
                         for command in self.commands]
        commandLine = '; '.join(self.commands)
        return subprocess.Popen(commandLine, shell=True)
