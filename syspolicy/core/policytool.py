#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import syspolicy.core.change
import syspolicy.core.config
from syspolicy.core.config import Config
from syspolicy.core.policy import Policy
from syspolicy.core.worker import Worker
from syspolicy.modules.module import Module

class PolicyTool:
    def __init__(self,  configfile):
        self.conf = Config("main_config", configfile)
        self.policy = {}
        self.state = {}
        self.handler = {}
        for type,  file in self.conf.get(['policy']).items():
            self.policy[type] = Policy(type, self.conf.get(['general', 'policy-path'])+'/'+file)
            try:
                self.state[type] = Policy(type, self.conf.get(['general', 'state-path'])+'/'+file)
            except IOError:
                self.state[type] = Policy(type, self.conf.get(['general', 'state-path'])+'/'+file,  False)
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
            if module.pt is None:
                module.pt = self
                self.module[module.name] = module
                self.module_locks[module.name] = threading.Lock()
                for policy_type,  attributes in module.handled_attributes.items():
                    for attribute in attributes:
                        self.register_handler(policy_type,  attribute,  module)
            else:
                print module, "has already been registered with", module.pt
    
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
        print "Diff:", diff
        for type, policy in diff.items():
            if type in self.handler:
                for group_name,  group in policy.items():
                    for attribute, value in group.items():
                        if attribute in self.handler[type]:
                            h = self.handler[type][attribute]
                            path = [group_name,  attribute]
                            print "Found a handler for", type, "->", path, ":", h
                            operation = syspolicy.core.config.diff_type(policy, self.state[type], path)
                            cs = h.pol_check_diff(self.policy[type].name, operation, path, value)
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
    
    def accept_changeset(self, changeset, accepted = True):
        if accepted == True:
            state = syspolicy.core.change.STATE_ACCEPTED
        else:
            state = syspolicy.core.change.STATE_REJECTED
        
        if changeset in self.changesets:
            with self.cs_locks[changeset]:
                changeset.set_state(state)
    
    def enqueue_changesets(self):
        with self.cs_mlock:
            for cs in self.changesets:
                with self.cs_locks[cs]:
                    if cs.state == syspolicy.core.change.STATE_ACCEPTED:
                        self.worker.queue.put(cs)
                        print "Adding ChangeSet", cs, "to the Worker's queue"
