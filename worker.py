import logging


class Worker(object):
    def __init__(self):

        self.job = None

    def addJob(self, job):

        if self.job and self.job.isRunning():
            return job

        self.job = job
        self.execute()

    def execute(self):
        if not self.job:
            return
        self.job.execute()

    def exit(self):
        if not self.job:
            return
        self.job.killProc()
