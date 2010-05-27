# SysPolicy
# 
# Copyright (c) 2010 Lenno Nagel
# Author: Lenno Nagel <lenno-at-nagel.ee>
# URL: <http://trac.syspolicy.org>
# Released under the GNU General Public License version 3

from __future__ import with_statement

import threading
from Queue import Queue
import syspolicy.change

class Worker(threading.Thread):
    def __init__(self, policytool):
        threading.Thread.__init__(self)
        self.daemon = True
        self.queue = Queue()
        self.log = Queue()
        self.pt = policytool
    
    def run(self):
        while True:
            cs = self.queue.get()
            with self.pt.get_cs_lock(cs):
                if self.pt.debug:
                    print "Worker processing ChangeSet", cs
                for c in cs.changes:
                    with self.pt.get_module_lock(c.subsystem):
                        module = self.pt.module[c.subsystem]
                        if self.pt.debug:
                            print "Worker processing Change", c, "with module", module.name, 
                        try:
                            c.state = module.perform_change(c)
                        except Exception, inst:
                            print "Worker encountered an exception while processing ChangeSet", cs, "\n", inst
                            c.state = syspolicy.change.STATE_FAILED
                        if self.pt.debug:
                            print "=>", syspolicy.change.state_string(c.state)
                        if c.state == syspolicy.change.STATE_FAILED:
                            break
                # let the ChangeSet update it's status:
                cs.get_state()
                if self.pt.debug:
                    print "This ChangeSet =>", syspolicy.change.state_string(cs.get_state())
                    print
            self.queue.task_done()
