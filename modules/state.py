
from module import Module
import core.config
import core.change
from core.change import Change, ChangeSet

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
        
        if diff_type in [core.config.CONFIG_ADDED, core.config.CONFIG_CHANGED]:
            self.pt.set_state(policy, path, value)
            return core.change.STATE_COMPLETED
        elif diff_type in [core.config.CONFIG_REMOVED]:
            self.pt.set_state(policy, path, None)
            return core.change.STATE_COMPLETED
        
        return core.change.STATE_FAILED
