
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
            
            if group == config.DEFAULT:
                print "assign default setting:", attribute, "=", value
            else:
                if operation == config.CONFIG_ADDED:
                    print "new", 
                elif operation == config.CONFIG_CHANGED:
                    print "changed", 
                elif operation == config.CONFIG_REMOVED:
                    print "removed", 
                
                print "group setting:", attribute, "=", value
            
        
        return None
