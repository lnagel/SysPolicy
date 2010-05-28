# SysPolicy
# 
# Copyright (c) 2010 Lenno Nagel
# Author: Lenno Nagel <lenno-at-nagel.ee>
# URL: <http://trac.syspolicy.org>
# Released under the GNU General Public License version 3

"""
SysPolicy's back-end module for user interfaces
"""

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
    """
    This is the main interface class for SysPolicy that's designed to be used
    from the user interface side, eg. from the CLI interface packages.
    
    This intends to provide all the features of the core library that need to
    be exposed to the developers of user interfaces or other software based
    on SysPolicy's functionality.
    """
    
    conf = None #: main configuration object (Config class instance)
    debug = False #: whether or not SysPolicy is running in debug mode
    policy = None #: dictionary of all the policies defined in the main conf
    state = None #: respective state objects for the policies
    handler = None #: attribute handlers for all the policies
    events = None #: event hooks by event type
    
    module = None #: loaded extension modules
    module_locks = None #: locks for the loaded modules
    
    changesets = None #: ChangeSets that have been proposed or worked on
    cs_mlock = None #: master lock for the changesets
    cs_locks = None #: dictionary of individial locks for all ChangeSets
    
    worker = None #: Worker instance for background processing of ChangeSets
    
    def __init__(self, configfile, debug=False):
        """
        Initialize the PolicyTool by loading the configuration and all policies,
        modules, setting up locking mechanisms and starting the background
        Worker process.
        """
        self.conf = Config("main_config", configfile)
        self.debug = debug
        self.policy = {}
        self.state = {}
        self.handler = {}
        self.events = {}
        
        # load all the policy and state files
        for type, file in self.conf.get(['policy']).items():
            self.policy[type] = Policy(type, self.conf.get(['general', 'policy-path'])+'/'+file, merge_default=True)
            try:
                self.state[type] = Policy(type, self.conf.get(['general', 'state-path'])+'/'+file)
            except IOError:
                self.state[type] = Policy(type, self.conf.get(['general', 'state-path'])+'/'+file, load=False)
                self.state[type].save()
        
        # initialize the modules and locks
        self.module = {}
        self.module_locks = {}
        self.changesets = []
        self.cs_mlock = threading.Lock()
        self.cs_locks = {}
        
        # initialize the background Worker
        self.worker = Worker(self)
        self.worker.start()
        
        # autoload the extension modules
        autoload_modules(self)
    
    def set_state(self, type, path, value):
        """
        This function updates the state of one of the policies.
        
        @param type: The policy in which the state is set
        @param path: The path to the changed value
        @param value: the new value
        """
        if type in self.state:
            self.state[type].set(path, value)
    
    def save_state(self):
        """
        This function saves the internal state for each policy.
        """
        for type, state in self.state.items():
            state.save()
    
    def clear_state(self):
        """
        This function clears all the internal states of all policies.
        """
        for type, state in self.state.items():
            state.clear()
    
    def add_module(self, module):
        """
        This function loads a new module to the PolicyTool.
        
        @param module: The module to be loaded. Must be an instance of the
            Module class or one of it's subclasses.
        """
        if isinstance(module, Module):
            if self.debug:
                print module, "is a module!"
            if module.pt is None:
                # in the case that the module hasn't been loaded to any other
                # PolicyTool, accept it and set up required variables and locks
                module.pt = self
                self.module[module.name] = module
                self.module_locks[module.name] = threading.Lock()
                
                # scan for handled attributes in the module and learn them
                for policy_type, attributes in module.handled_attributes.items():
                    for attribute in attributes:
                        self.register_attribute_handler(policy_type, attribute, module)
                
                # scan for event hooks and learn them
                for event, handler in module.event_hooks.items():
                    self.register_event_handler(event, handler)
            else:
                print module, "has already been registered with", module.pt
    
    def register_attribute_handler(self, policy_type, attribute, module):
        """
        This function registers a new attribute handler for a module.
        
        In case the attribute has already been assigned a handler,
        an exception is raised and the this request is refused.
        
        @param policy_type: The type (name) of the policy of the attribute
        @param attribute: The name of the handled attribute
        @param module: The Module instance claiming the attribute
        """
        if policy_type not in self.handler:
            self.handler[policy_type] = {}
        if attribute not in self.handler[policy_type]:
            self.handler[policy_type][attribute] = module
            if self.debug:
                print "Registered handler: policy", policy_type, "attribute", attribute, "to", module
        else:
            raise Exception("Handler has already been set for policy '" + policy_type + "' attribute '" + attribute + "'")
    
    def register_event_handler(self, event, handler):
        """
        This function registers a new event hook for the event type `event`.
        There can be many hooks for the same event type.
        
        @param event: The event which is hooked into
        @param handler: The function that must be called when the event fires
        """
        # create a list if it doesn't already exist
        if event not in self.events:
            self.events[event] = []
            
        # append the handler function
        self.events[event].append(handler)
        
        if self.debug:
            print "Registered event", str(event), "to", handler
    
    def emit_event(self, event, changeset=None):
        """
        This function emits an event of type `event`, calling all the
        registered handler functions for this event type.
        
        @param event: Type of the event that is being emitted
        @param changeset: A ChangeSet that is triggering the event
        """
        if event in self.events:
            for handler in self.events[event]:
                handler(event, changeset)
    
    def get_policy_diff(self):
        """
        This function returns the difference between the policies and
        their previously known states, finding changed values.
        
        @return: Difference between all policies and their saved states
        """
        diff = {}
        for type in self.policy:
            diff[type] = self.policy[type].compare_to(self.state[type])
        return diff
    
    def get_policy_updates(self):
        """
        This function returns a list of ChangeSets that must be implemented to
        accommodate the changes the user has made to the policy files.
        
        The function works by detecting the policy differences and handling
        each difference with the registered attribute handler module. Each
        handler call may return a ChangeSet which is then recorded.
        
        @return: A list of ChangeSet elements
        """
        # get the full policy difference from the last known state
        diff = self.get_policy_diff()
        # set up a fallback module when the attribute doesn't have a handler
        fallback = self.module['state']
        
        if self.debug:
            print "Diff:", diff
        
        # iterate all the policies in the diff
        for type, policy in diff.items():
            # iterate all the groups in the policy
            for group_name, group in policy.items():
                # iterate each changed attribute in the group
                for attribute, valuediff in group.items():
                    # find the handler for this attribute, or use the fallback
                    if type in self.handler:
                        h = self.handler[type].get(attribute, fallback)
                    else:
                        h = fallback
                    
                    # record the attribute path
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
                    
                    # call the difference handler for this attribute
                    cs = h.cs_check_diff(self.policy[type].name, operation, path, value, valuediff)
                    
                    # record the ChangeSet, if there is any
                    if cs is not None:
                        self.add_changeset(cs)
                    if self.debug:
                        print "-" * 40
        
        return self.changesets
    
    def get_cs_lock(self, changeset):
        """
        This function returns the Lock object for a known ChangeSet.
        
        @param changeset: The ChangeSet for which the Lock is to be obtained
        @return: A Lock object or None if not found
        """
        return self.cs_locks.get(changeset,  None)
    
    def get_module_lock(self, module_name):
        """
        This function returns a Lock object for the given module.
        
        @param module_name: The module for which the Lock is to be obtained
        @return: A Lock objet or None if not found
        """
        return self.module_locks.get(module_name, None)

    def add_changeset(self, changeset):
        """
        This function appends a new ChangeSet to the list.
        Additionally, a threading.Lock object is created for this ChangeSet.
        
        @param changeset: The new ChangeSets
        """
        with self.cs_mlock:
            self.changesets.append(changeset)
            self.cs_locks[changeset] = threading.Lock()
    
    def accept_changeset(self, changeset, accepted=True):
        """
        This module updates the state of a ChangeSet to either
        be STATE_ACCEPTED if accepted is True or STATE_REJECTED
        otherwise.
        
        @param changeset: The ChangeSet which's status is changed
        @param accepted: Whether the ChangeSet is accepted or not
        """
        if accepted == True:
            state = syspolicy.change.STATE_ACCEPTED
        else:
            state = syspolicy.change.STATE_REJECTED
        
        if changeset in self.changesets:
            with self.cs_locks[changeset]:
                changeset.set_state(state)
    
    def accept_state_changes(self):
        """
        This function automatically accepts all proposed ChangeSets that
        contain only 'set_state' operations in the 'state' subsystem.
        
        This can be called to auto-accept all policy changes that don't need
        any review from the user's side.
        """
        with self.cs_mlock:
            for cs in self.changesets:
                statechange = False
                with self.cs_locks[cs]:
                    # iterate the changes and see if they are only state changes
                    for c in cs.changes:
                        if c.subsystem == 'state' and c.operation == 'set_state':
                            statechange = True
                        else:
                            statechange = False
                            break
                # in case there are only state changes, accept this ChangeSet
                if statechange:
                    self.accept_changeset(cs, True)
    
    def changesets_with_state(self, state):
        """
        This function queries the stored list of ChangeSet for the ones
        with the state `state` and returns this list. For example, it can be
        used to find all the accepted ChangeSets like this:
        
        pt.changesets_with_state(syspolicy.change.STATE_ACCEPTED)
        
        @param state: The state which is being matched to ChangeSets
        @return: A list of ChangeSets with the state `state`
        """
        results = []
        with self.cs_mlock:
            # iterate all ChangeSets
            for cs in self.changesets:
                with self.cs_locks[cs]:
                    # match the ChangeSet's current state
                    if cs.get_state() == state:
                        results.append(cs)
        return results
    
    def enqueue_changesets(self, changesets):
        """
        This function enqueue's the provided ChangeSets with the Worker.
        
        @param changesets: A list of ChangeSets for processing
        """
        for cs in changesets:
            self.worker.queue.put(cs)
            if self.debug:
                print "Adding ChangeSet", cs, "to the Worker's queue"
