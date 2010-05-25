#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import threading
import syspolicy.change
import syspolicy.config
from syspolicy.config import Config
from syspolicy.policy import Policy
from syspolicy.worker import Worker
from syspolicy.modules.module import Module
from syspolicy.modules.autoloader import autoload_modules

class PolicyTool:
    def __init__(self, configfile, debug=False):
        self.conf = Config("main_config", configfile)
        self.debug = debug
        self.policy = {}
        self.state = {}
        self.handler = {}
        self.events = {}
        for type, file in self.conf.get(['policy']).items():
            self.policy[type] = Policy(type, self.conf.get(['general', 'policy-path'])+'/'+file, merge_default=True)
            try:
                self.state[type] = Policy(type, self.conf.get(['general', 'state-path'])+'/'+file)
            except IOError:
                self.state[type] = Policy(type, self.conf.get(['general', 'state-path'])+'/'+file, load=False)
                self.state[type].save()
        self.module = {}
        self.module_locks = {}
        self.changesets = []
        self.cs_mlock = threading.Lock()
        self.cs_locks = {}
        
        self.worker = Worker(self)
        self.worker.start()
        
        autoload_modules(self)
    
    def set_state(self, type, path, value):
        if type in self.state:
            self.state[type].set(path, value)
    
    def save_state(self):
        for type, state in self.state.items():
            state.save()
    
    def clear_state(self):
        for type, state in self.state.items():
            state.clear()
    
    def add_module(self, module):
        if isinstance(module, Module):
            if self.debug:
                print module, "is a module!"
            if module.pt is None:
                module.pt = self
                self.module[module.name] = module
                self.module_locks[module.name] = threading.Lock()
                for policy_type, attributes in module.handled_attributes.items():
                    for attribute in attributes:
                        self.register_attribute_handler(policy_type, attribute, module)
                for event, handler in module.event_hooks.items():
                    self.register_event_handler(event, handler)
            else:
                print module, "has already been registered with", module.pt
    
    def register_attribute_handler(self, policy_type, attribute, module):
        if policy_type not in self.handler:
            self.handler[policy_type] = {}
        if attribute not in self.handler[policy_type]:
            self.handler[policy_type][attribute] = module
            if self.debug:
                print "Registered handler: policy", policy_type, "attribute", attribute, "to", module
        else:
            raise Exception("Handler has already been set for policy '" + policy_type + "' attribute '" + attribute + "'")
    
    def register_event_handler(self, event, handler):
        if event not in self.events:
            self.events[event] = []
        self.events[event].append(handler)
        if self.debug:
            print "Registered event", str(event), "to", handler
    
    def emit_event(self, event, changeset=None):
        if event in self.events:
            for handler in self.events[event]:
                handler(event, changeset)
    
    def get_policy_diff(self):
        diff = {}
        for type in self.policy:
            diff[type] = self.policy[type].compare_to(self.state[type])
        return diff
    
    def get_policy_updates(self):
        diff = self.get_policy_diff()
        fallback = self.module['state']
        if self.debug:
            print "Diff:", diff
        for type, policy in diff.items():
            for group_name, group in policy.items():
                for attribute, valuediff in group.items():
                    if type in self.handler:
                        h = self.handler[type].get(attribute, fallback)
                    else:
                        h = fallback
                    path = [group_name, attribute]
                    if self.debug:
                        print "Handler for", type, "->", path, ":", h
                    # check if the whole group was removed
                    if group_name not in self.policy[type].data:
                        value = None
                        operation = syspolicy.config.CONFIG_REMOVED
                    else:
                        value = self.policy[type].get(path)
                        operation = syspolicy.config.diff_type(policy, self.state[type], path)
                    cs = h.cs_check_diff(self.policy[type].name, operation, path, value, valuediff)
                    if cs is not None:
                        self.add_changeset(cs)
                    if self.debug:
                        print "-" * 40
        return self.changesets
    
    def get_cs_lock(self, changeset):
        cs_lock = None
        with self.cs_mlock:
            cs_lock = self.cs_locks[changeset]
        return cs_lock
    
    def get_module_lock(self, module_name):
        return self.module_locks[module_name]

    def add_changeset(self, changeset):
        with self.cs_mlock:
            self.changesets.append(changeset)
            self.cs_locks[changeset] = threading.Lock()
    
    def accept_changeset(self, changeset, accepted=True):
        if accepted == True:
            state = syspolicy.change.STATE_ACCEPTED
        else:
            state = syspolicy.change.STATE_REJECTED
        
        if changeset in self.changesets:
            with self.cs_locks[changeset]:
                changeset.set_state(state)
    
    def accept_state_changes(self):
        with self.cs_mlock:
            for cs in self.changesets:
                statechange = False
                with self.cs_locks[cs]:
                    for c in cs.changes:
                        if c.subsystem == 'state' and c.operation == 'set_state':
                            statechange = True
                        else:
                            statechange = False
                            break
                if statechange:
                    self.accept_changeset(cs, True)
    
    def changesets_with_state(self, state):
        results = []
        with self.cs_mlock:
            for cs in self.changesets:
                with self.cs_locks[cs]:
                    if cs.state == state:
                        results.append(cs)
        return results
    
    def enqueue_changesets(self, changesets):
        for cs in changesets:
            self.worker.queue.put(cs)
            if self.debug:
                print "Adding ChangeSet", cs, "to the Worker's queue"
