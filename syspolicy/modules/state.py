
import syspolicy.config
import syspolicy.change
from syspolicy.change import Change, ChangeSet
from syspolicy.modules.module import Module

class State(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "state"
        self.change_operations['set_state'] = self.set_state

    def set_state(self, change):
        policy = change.parameters['policy']
        path = change.parameters['path']
        diff_type = change.parameters['diff_type']
        value = change.parameters['value']
        
        if diff_type in [syspolicy.config.CONFIG_ADDED, syspolicy.config.CONFIG_CHANGED]:
            self.pt.set_state(policy, path, value)
            return syspolicy.change.STATE_COMPLETED
        elif diff_type in [syspolicy.config.CONFIG_REMOVED]:
            self.pt.set_state(policy, path, None)
            return syspolicy.change.STATE_COMPLETED
        
        return syspolicy.change.STATE_FAILED
