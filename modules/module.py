
import core.config as config
import core.change

class Module:
    def __init__(self):
        self.name = "generic"
        self.handled_attributes = {}
        self.diff_operations = {
                            config.CONFIG_ADDED: self.pol_new_attribute,
                            config.CONFIG_CHANGED: self.pol_set_attribute,
                            config.CONFIG_REMOVED: self.pol_rem_attribute
                        }

    def pol_check_diff(self, policy,  state, path, value):
        print "pol_check_diff for",  path, ",", value
        if len(path) >= 2:
            group = path[0]
            attribute = path[1]
            operation = config.diff_type(policy,  state,  path)
            cs = None
            
            if group == config.DEFAULT:
                print "assign default setting:", attribute, "=", value
                cs = self.pol_set_default(attribute, value)
            elif operation in self.diff_operations:
                cs = self.diff_operations[operation](group, attribute, value)
        
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
        return core.change.STATE_IGNORED
    
    
