
import core.config as config
import core.change

class Module:
    def __init__(self):
        self.name = "generic"
        self.handled_attributes = {}

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
            else:
                if operation == config.CONFIG_ADDED:
                    print "new", "group setting:", attribute, "=", value
                    cs =self.pol_new_attribute(group, attribute, value)
                elif operation == config.CONFIG_CHANGED:
                    print "changed", "group setting:", attribute, "=", value
                    cs = self.pol_set_attribute(group, attribute, value)
                elif operation == config.CONFIG_REMOVED:
                    print "removed", "group setting:", attribute, "=", value
                    cs = self.pol_rem_attribute(group, attribute)
        
        return cs

    def pol_set_default(self, attribute, value):
        return None
    
    def  pol_new_attribute(self, group, attribute, value):
        return self.pol_set_attribute(group, attribute, value)
    
    def pol_set_attribute(self, group, attribute, value):
        return None
    
    def pol_rem_attribute(self, group, attribute):
        return None
    
    def perform_change(self, change):
        return core.change.STATE_IGNORED
    
    
