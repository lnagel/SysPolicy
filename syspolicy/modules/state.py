
import syspolicy.config
import syspolicy.change
from syspolicy.change import Change, ChangeSet
from syspolicy.modules.module import Module

class State(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "state"
        self.change_operations['set_state'] = self.set_state
    
    def cs_check_diff(self, policy, operation, path, value, diff):
        state_update = Change(self.name, "set_state", 
                             {"policy": policy, "path": path,
                                "value": value, "diff_type": operation})
        return ChangeSet(state_update)
    
    def set_state(self, change):
        p = change.parameters
        policy = p['policy']
        path = p['path']
        diff_type = p['diff_type']
        value = p['value']
        
        if diff_type in [syspolicy.config.CONFIG_ADDED, syspolicy.config.CONFIG_CHANGED]:
            self.pt.set_state(policy, path, value)
            return syspolicy.change.STATE_COMPLETED
        elif diff_type in [syspolicy.config.CONFIG_REMOVED]:
            self.pt.set_state(policy, path, None)
            return syspolicy.change.STATE_COMPLETED
        
        return syspolicy.change.STATE_FAILED
