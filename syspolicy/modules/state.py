
import syspolicy.core.config
import syspolicy.core.change
from syspolicy.core.change import Change, ChangeSet
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
        
        if diff_type in [syspolicy.core.config.CONFIG_ADDED, syspolicy.core.config.CONFIG_CHANGED]:
            self.pt.set_state(policy, path, value)
            return syspolicy.core.change.STATE_COMPLETED
        elif diff_type in [syspolicy.core.config.CONFIG_REMOVED]:
            self.pt.set_state(policy, path, None)
            return syspolicy.core.change.STATE_COMPLETED
        
        return syspolicy.core.change.STATE_FAILED
