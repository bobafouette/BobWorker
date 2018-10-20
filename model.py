import subprocess
import json


class Job(object):

    PROTOCOL_FLAG = "JOB"

    @staticmethod
    def readDesc(desc):

        desc = json.loads(desc)
        job = Job(desc["name"], desc["metadata"])
        job.addCommands([" ".join(command) for command in desc["commands"]])
        return job

    def __init__(self, name, metadata={}):
        self._name = name
        self.commands = []
        if not metadata:
            metadata = {}
        self.metadata = metadata
        self.proc = None

        # Used once the job is completed
        self.rcode = None
        self.stdin = None
        self.stderr = None

    def isRunning(self):
        if self.proc:
            self.rcode = self.proc.poll()
            if self.rcode is None:
                return True
            self.stdout = self.proc.stdout.read()
            self.stderr = self.proc.stderr.read()
            self.proc = None
            return False
        return True

    def killProc(self):
        if not self.isRunning():
            return
        self.proc.kill()
        self.rcode = self.proc.returncode
        self.stdout = self.proc.stdout.read()
        self.stderr = self.proc.stderr.read()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def writeDesc(self):
        desc = {
            # TODO: Why casting as list?
            "commands": [list(command.split(" ")) for command in self.commands],
            "name": self.name,
            "metadata": self.metadata,
        }
        return json.dumps(desc)

    def addCommands(self, commands):
        if not isinstance(commands, list):
            commands = [commands]
        self.commands.extend(commands)

    def execute(self):
        self.commands = [command.format(**self.metadata) for command in self.commands]
        commandLine = "; ".join(self.commands)
        self.proc = subprocess.Popen(commandLine, shell=True)
