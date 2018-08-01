from threading import RLock


class Worker(object):


    def __init__(self):

        self.job= None
        self.proc = None
        self.lock = RLock()


    def addJob(self, job):
        
        self.lock.acquire()
        print('Testing state')
        if self.job or (self.proc and self.proc.poll() is None):
            return job
        
        if self.proc:
            self.proc = None
        
        self.job = job
        self.execute()
        self.lock.release()


    def execute(self):
        if not self.job:
            return
        
        job = self.job
        self.job = None
        self.proc = job.execute()
