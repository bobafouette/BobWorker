import logging
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

    def __init__(self, name, metadata=None):
        self._name = name
        self.commands = []
        if not metadata:
            metadata = {}
        self.metadata = metadata
        self.proc = None

        logging.getLogger(self.__class__.__name__).setLevel(logging.INFO)

    def isRunning(self):
        if not self.proc:
            return False

        if self.proc.poll() is None:
            return True

        self.notifyEnded()
        return False

    def killProc(self):
        if not self.isRunning():
            return
        self.proc.kill()
        self.notifyEnded()

    def notifyEnded(self):
        self.proc = None

        if not self.proc or not self.proc.returncode:
            logging.getLogger(self.__class__.__name__).warning(
                "The method Job.notifyEndend has been called on a running job"
            )
            return

        # Setup log message
        if self.proc.returncode != 0:
            # Error warning
            state = "in error (rcode {rcode})".format(self.proc.returncode)
            logLevel = logging.WARNING
        else:
            # Done info
            state = "done"
            logLevel = logging.INFO
        # The outputs
        stdout = self.proc.stdout.read()
        stderr = self.proc.stderr.read()

        message = [
            "The Job {name} is {state}.".format(name=self.name, state=state),
            "\t-stdout:{stdout}.".format(stdout=stdout),
            "\t-stderr: {stderr}".format(stderr=stderr),
        ]
        for line in message:
            logging.getLogger(self.__class__.__name__).log(logLevel, line)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def writeDesc(self):
        desc = {
            "commands": [command.split(" ") for command in self.commands],
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
