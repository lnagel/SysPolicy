
import core.config as config

class Module:
    def __init__(self):
        self.name = "generic"
        self.handled_attributes = {}

    def check_diff(self, policy,  state, path, value):
        print "check_diff for",  path, ",", value
        if len(path) >= 2:
            group = path[0]
            attribute = path[1]
            operation = config.diff_type(policy,  state,  path)
            cs = None
            
            if group == config.DEFAULT:
                print "assign default setting:", attribute, "=", value
                cs = self.set_default(attribute, value)
            else:
                if operation == config.CONFIG_ADDED:
                    print "new", "group setting:", attribute, "=", value
                    cs =self.new_attribute(group, attribute, value)
                elif operation == config.CONFIG_CHANGED:
                    print "changed", "group setting:", attribute, "=", value
                    cs = self.set_attribute(group, attribute, value)
                elif operation == config.CONFIG_REMOVED:
                    print "removed", "group setting:", attribute, "=", value
                    cs = self.rem_attribute(group, attribute)
        
        return cs

    def set_default(self, attribute, value):
        return None
    
    def  new_attribute(self, group, attribute, value):
        return self.set_attribute(group, attribute, value)
    
    def set_attribute(self, group, attribute, value):
        return None
    
    def rem_attribute(self, group, attribute):
        return None
    
    
