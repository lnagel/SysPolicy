

import threading
from Queue import Queue

class Worker(threading.Thread):
    def __init__(self, policytool):
        threading.Thread.__init__(self)
        self.daemon = True
        self.queue = Queue()
        self.log = Queue()
        self.pt = policytool
    
    def run(self):
        print "== Worker started =="
        while True:
            cs = self.queue.get()
            with self.pt.get_cs_lock(cs):
                print "Worker processing ChangeSet", cs
            self.queue.task_done()
