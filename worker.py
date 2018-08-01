class Worker(object):


    def __init__(self):

        self.job= None
        self.proc = None


    def addJob(self, job):
        
        print('Testing state')
        if self.job or (self.proc and self.proc.poll() is None):
            return job
        
        if self.proc:
            self.proc = None
        
        self.job = job
        self.execute()


    def execute(self):
        if not self.job:
            return
        
        job = self.job
        self.job = None
        self.proc = job.execute()
