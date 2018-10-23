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

        if not self.proc:
            logging.getLogger(self.__class__.__name__).warning(
                "The method Job.notifyEndend has been called on a procless job"
            )
            return

        if self.proc.returncode is None:
            logging.getLogger(self.__class__.__name__).warning(
                "The method Job.notifyEndend has been called on a running job"
            )
            return

        # Clean proc attribute
        proc = self.proc
        self.proc = None

        # Setup log message
        if proc.returncode != 0:
            # Error warning
            state = "in error (rcode {rcode})".format(proc.returncode)
            logLevel = logging.WARNING
        else:
            # Done info
            state = "done"
            logLevel = logging.INFO
        # The outputs
        stdout = proc.stdout.read()
        stderr = proc.stderr.read()

        message = "\n".join(
            ["The Job {name} is {state}.", "\t-stdout:{stdout}.", "\t-stderr: {stderr}"]
        ).format(name=self.name, state=state, stdout=stdout, stderr=stderr)
        logging.getLogger(self.__class__.__name__).log(logLevel, message)

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
        self.proc = subprocess.Popen(
            commandLine, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )
