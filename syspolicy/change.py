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
    if state in _state_strings:
        return _state_strings[state]
    else:
        return ''

class Change:
    def __init__(self, subsystem, operation, parameters):
        self.subsystem = subsystem
        self.operation = operation
        self.parameters = parameters
        self.state = STATE_PROPOSED

class ChangeSet:
    def __init__(self, changes=None):
        self.changes = []
        self.state = STATE_PROPOSED
        if changes is not None:
            if type(changes) is list:
                self.changes.extend(changes)
            elif isinstance(changes, Change):
                self.changes.append(changes)
    
    def set_state(self, state):
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
        if self.state == STATE_ACCEPTED:
            for change in self.changes:
                if change.state == STATE_ACCEPTED:
                    return
                elif change.state not in [STATE_COMPLETED, STATE_NOT_HANDLED]:
                    self.state = STATE_FAILED
                    return
            self.state = STATE_COMPLETED

    def get_state(self):
        self.check_state()
        return self.state
    
    def append(self, change):
        self.changes.append(change)
    
    def insert(self, position, change):
        self.changes.insert(position, change)
    
    def extend(self, changes):
        self.changes.extend(changes)
    
    def merge(self, changeset):
        self.changes.extend(changeset.changes)
