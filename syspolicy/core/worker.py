
import threading
from Queue import Queue
import syspolicy.core.change

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
                for c in cs.changes:
                    with self.pt.get_module_lock(c.subsystem):
                        module = self.pt.module[c.subsystem]
                        print "Worker processing Change", c, "with module", module.name, 
                        c.state = module.perform_change(c)
                        print "=>", syspolicy.core.change.state_string(c.state)
                        if c.state == syspolicy.core.change.STATE_FAILED:
                            break
                print "This ChangeSet =>", syspolicy.core.change.state_string(cs.get_state())
                print
            self.queue.task_done()
