
import syspolicy.core.config
import syspolicy.core.change
from syspolicy.core.change import Change, ChangeSet

class Module:
    def __init__(self):
        self.name = "generic"
        self.handled_attributes = {}
        self.pt = None
        self.diff_operations = {
                            syspolicy.core.config.CONFIG_ADDED: self.pol_new_attribute,
                            syspolicy.core.config.CONFIG_CHANGED: self.pol_set_attribute,
                            syspolicy.core.config.CONFIG_REMOVED: self.pol_rem_attribute
                        }
        self.change_operations = {}

    def pol_check_diff(self, policy, operation, path, value):
        print "pol_check_diff in:", policy, "operation:", operation, "for:",  path, ",", value
        cs = None
        state_update = Change("state", "set_state", 
                             {"policy": policy, "path": path,
                             "value": value, "diff_type": operation})
     
        if len(path) >= 2:
            group = path[0]
            attribute = path[1]
            
            if group == syspolicy.core.config.DEFAULT:
                print "assign default setting:", attribute, "=", value
                cs = self.pol_set_default(attribute, value)
            elif operation in self.diff_operations:
                cs = self.diff_operations[operation](group, attribute, value)
        
        if cs is not None:
            cs.append(state_update)
        else:
            cs = ChangeSet(state_update)
        
        return cs

    def pol_set_default(self, attribute, value):
        return None
    
    def  pol_new_attribute(self, group, attribute, value):
        return self.pol_set_attribute(group, attribute, value)
    
    def pol_set_attribute(self, group, attribute, value):
        return None
    
    def pol_rem_attribute(self, group, attribute, value = None):
        return None
    
    def perform_change(self, change):
        if change.operation in self.change_operations:
            return self.change_operations[change.operation](change)
        else:
            return syspolicy.core.change.STATE_NOT_HANDLED
    
    
