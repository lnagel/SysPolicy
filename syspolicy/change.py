# SysPolicy
# 
# Copyright (c) 2010 Lenno Nagel
# Author: Lenno Nagel <lenno-at-nagel.ee>
# URL: <http://trac.syspolicy.org>
# Released under the GNU General Public License version 3

"""
Change management classes
"""

STATE_UNKNOWN = 0
STATE_PROPOSED = 1
STATE_ACCEPTED = 2
STATE_REJECTED = 3
STATE_IGNORED = 4
STATE_NOT_HANDLED = 8
STATE_COMPLETED = 9
STATE_FAILED = 10

_state_strings = {
    STATE_UNKNOWN: 'unknown', 
    STATE_PROPOSED: 'proposed', 
    STATE_ACCEPTED: 'accepted', 
    STATE_REJECTED: 'rejected', 
    STATE_IGNORED: 'ignored', 
    STATE_NOT_HANDLED: 'not handled', 
    STATE_COMPLETED: 'completed', 
    STATE_FAILED: 'failed'
}

def state_string(state):
    """
    This function returns the string representation (description) for a given
    numerical state or '' if the state isn't recognized.
    """
    if state in _state_strings:
        return _state_strings[state]
    else:
        return ''

class Change:
    """
    This class represents a Change element for keeping track of the actions
    that need to be performed on the system. Contains no logic, only data.
    """
    subsystem = None #: indicates the module that implements the Change
    operation = None #: indicates the change operation function
    parameters = None #: dictionary of parameters for the operation
    state = STATE_UNKNOWN #: current state of the operation
    
    def __init__(self, subsystem, operation, parameters):
        self.subsystem = subsystem
        self.operation = operation
        self.parameters = parameters
        self.state = STATE_PROPOSED

class ChangeSet:
    """
    This class represents a set of Change's that are to be implemented in
    the order they are appended to the ChangeSet. A ChangeSet is considered
    completed only when all the changes have been completed successfully.
    
    A ChangeSet must be either accepted or rejected in it's entirety and no
    individual selection among the Change's is supported. This is a design
    requirement, since many times Changes depend on the previous ones.
    """
    
    changes = None #: an ordered list of Change elements creating the ChangeSet
    state = STATE_UNKNOWN #: summarized state of the ChangeSet
    
    def __init__(self, changes=None):
        self.changes = []
        self.state = STATE_PROPOSED
        
        # load any Changes that were passed to the constructor
        if changes is not None:
            if type(changes) is list:
                self.changes.extend(changes)
            elif isinstance(changes, Change):
                self.changes.append(changes)
    
    def set_state(self, state):
        """
        This function accepts a new state for the ChangeSet and 
        marks this state for all the contained Changes as well.
        
        If the current state is STATE_PROPOSED, it can be changed to
        STATE_ACCEPTED, STATE_IGNORED or STATE_REJECTED.
        
        If the current state is STATE_ACCEPTED, it can be changed to
        STATE_COMPLETED or STATE_FAILED.
        
        @param state: The new state
        @return: True if the state of the ChangeSet is `state`, False otherwise
        """
        if self.state == STATE_PROPOSED:
            if state in [STATE_ACCEPTED, STATE_IGNORED, STATE_REJECTED]:
                for change in self.changes:
                    change.state = state
                self.state = state
        elif self.state == STATE_ACCEPTED:
            if self.state in [STATE_COMPLETED, STATE_FAILED]:
                self.state = state
        return (self.state == state)
    
    def check_state(self):
        """
        This function checks the state of the changes and updates the state
        of the ChangeSet if appropriate. The checking is performed only when
        the ChangeSet has been accepted.
        
        The state is changed to completed when all the changes have been
        completed and the state is changed to failed when a change is found
        that is not in the completed nor unhandled state.
        """
        if self.state == STATE_ACCEPTED:
            for change in self.changes:
                if change.state == STATE_ACCEPTED:
                    return
                elif change.state not in [STATE_COMPLETED, STATE_NOT_HANDLED]:
                    self.state = STATE_FAILED
                    return
            self.state = STATE_COMPLETED

    def get_state(self):
        """
        This function returns the state of the ChangeSet after checking it with
        self.check_state().
        """
        self.check_state()
        return self.state
    
    def append(self, change):
        """
        This function appends a Change to the ChangeSet.
        
        @param change: The Change to be appended
        """
        self.changes.append(change)
    
    def insert(self, position, change):
        """
        This function inserts a Change to the ChangeSet at position `position`.
        
        @param position: The position in the list of changes
        @param change: The Change to be appended
        """        
        self.changes.insert(position, change)
    
    def extend(self, changes):
        """
        This function extends the ChangeSet with a list of changes.
        
        @param changes: List of Change elements
        """
        self.changes.extend(changes)
    
    def merge(self, changeset):
        """
        This function merges the changes from another ChangeSet.
        
        @param changeset: Another ChangeSet where to get the Changes from
        """
        self.changes.extend(changeset.changes)
