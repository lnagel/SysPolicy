# SysPolicy
# 
# Copyright (c) 2010 Lenno Nagel
# Author: Lenno Nagel <lenno-at-nagel.ee>
# URL: <http://trac.syspolicy.org>
# Released under the GNU General Public License version 3

"""
Worker that implements ChangeSets in the background
"""

from __future__ import with_statement

import threading
from Queue import Queue
import syspolicy.change

class Worker(threading.Thread):
    """
    This class is the background worker thread for SysPolicy.
    
    It will implement all the ChangeSets that are enqueued and update
    their status according to the success or failure.
    """
    
    queue = None #: the queue of ChangeSets that need processing
    pt = None #: reference to the PolicyTool of this Worker
    
    def __init__(self, policytool):
        """
        Initialize the Worker and it's Queues.
        
        @param policytool: The PolicyTool instance in which the Worker belongs
        """
        threading.Thread.__init__(self)
        self.daemon = True
        self.queue = Queue()
        self.log = Queue()
        self.pt = policytool
    
    def run(self):
        """
        This is the main function of the Worker class in which any queued
        ChangeSets are processed. This function runs in a separate daemon
        thread in the background.
        """
        
        # run forever
        while True:
            # get a ChangeSet from the queue
            cs = self.queue.get()
            
            # lock the ChangeSet during processing
            with self.pt.get_cs_lock(cs):
                if self.pt.debug:
                    print "Worker processing ChangeSet", cs
                
                # iterate the Changes in the ChangeSet
                for c in cs.changes:
                    # lock the module that this Change requires
                    with self.pt.get_module_lock(c.subsystem):
                        module = self.pt.module[c.subsystem]
                        if self.pt.debug:
                            print "Worker processing Change", c, "with module", module.name,
                        
                        # try to implement the Change
                        try:
                            c.state = module.perform_change(c)
                        except Exception, inst:
                            # in case it fails, print the error message
                            print "Worker encountered an exception while processing ChangeSet", cs, "\n", inst
                            # set the state as STATE_FAILED
                            c.state = syspolicy.change.STATE_FAILED
                        
                        if self.pt.debug:
                            print "=>", syspolicy.change.state_string(c.state)
                        
                        # halt processing of the ChangeSet if there's a failure
                        if c.state == syspolicy.change.STATE_FAILED:
                            break
                
                # let the ChangeSet update it's status:
                cs.check_state()
                
                if self.pt.debug:
                    print "This ChangeSet =>", syspolicy.change.state_string(cs.get_state())
                    print
            
            # report the ChangeSet as processed
            self.queue.task_done()
