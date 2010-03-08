

import threading
from Queue import Queue

class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.queue = Queue()
        self.log = Queue()
    
    def run(self):
        print "== Worker started =="
        while True:
            cs = self.queue.get()
            print "Worker processing ChangeSet", cs
            self.queue.task_done()
