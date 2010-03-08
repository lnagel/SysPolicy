#!/usr/bin/python
# -*- coding: utf-8 -*-

from config import Config
from policy import Policy
from modules import Module
from core.worker import Worker
import core.change
import threading
import time

class PolicyTool:
    def __init__(self,  configfile):
        self.conf = Config(configfile)
        self.policy = {}
        self.state = {}
        self.handler = {}
        for type,  file in self.conf.get(['policy']).items():
            self.policy[type] = Policy(self.conf.get(['general', 'policy-path'])+'/'+file)
            try:
                self.state[type] = Policy(self.conf.get(['general', 'state-path'])+'/'+file)
            except IOError:
                self.state[type] = Policy(self.conf.get(['general', 'state-path'])+'/'+file,  False)
                self.state[type].save()
        self.module = {}
        self.module_locks = {}
        self.changesets = []
        self.cs_mlock = threading.Lock()
        self.cs_locks = {}
        
        self.worker = Worker(self)
        self.worker.start()
    
    def set_state(self, type, path, value):
        if type in self.state:
            self.state[type].set(path, value)
    
    def save_state(self):
        for type, state in self.state.items():
            state.save()
    
    def add_module(self,  module):
        if isinstance(module, Module):
            print module,  "is a module!"
            self.module[module.name] = module
            self.module_locks[module.name] = threading.Lock()
            for policy_type,  attributes in module.handled_attributes.items():
                for attribute in attributes:
                    self.register_handler(policy_type,  attribute,  module)
    
    def register_handler(self,  policy_type,  attribute,  module):
        if policy_type not in self.handler:
            self.handler[policy_type] = {}
        if attribute not in self.handler[policy_type]:
            self.handler[policy_type][attribute] = module
            print "Registered handler: policy",  policy_type,  "attribute",  attribute,  "to",  module
        else:
            raise Exception("Handler has already been set for policy '" + policy_type + "' attribute '" + attribute + "'")
    
    def get_policy_diff(self):
        diff = {}
        for type in self.policy:
            diff[type] = self.policy[type].compare_to(self.state[type])
        return diff
    
    def get_policy_updates(self):
        diff = self.get_policy_diff()
        for type, policy in diff.items():
            if type in self.handler:
                for group_name,  group in policy.items():
                    for attribute, value in group.items():
                        if attribute in self.handler[type]:
                            print "Found a handler for", type, "->", group_name, "->", attribute, ":", self.handler[type][attribute]
                            cs = self.handler[type][attribute].check_diff(policy, self.state[type],  [group_name,  attribute],  value)
                            if cs is not None:
                                self.add_changeset(cs)
                        else:
                            print "Didn't find a handler for", type, "->", group_name, "->", attribute
                        print "-" * 40
        return self.changesets
    
    def get_cs_lock(self,  changeset):
        cs_lock = None
        with self.cs_mlock:
            cs_lock = self.cs_locks[changeset]
        return cs_lock
    
    def get_module_lock(self,  module_name):
        return self.module_locks[module_name]

    def add_changeset(self,  changeset):
        with self.cs_mlock:
            self.changesets.append(changeset)
            self.cs_locks[changeset] = threading.Lock()
    
    def enqueue_changesets(self):
        with self.cs_mlock:
            for cs in self.changesets:
                with self.cs_locks[cs]:
                    if cs.state == core.change.STATE_ACCEPTED:
                        self.worker.queue.put(cs)
                        print "Adding ChangeSet", cs, "to the Worker's queue"
                        time.sleep(1)


