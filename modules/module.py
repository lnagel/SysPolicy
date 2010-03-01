
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
                print operation, "default setting:", attribute, "=", value
            else:
                print operation, "group setting", attribute, "=", value
            
        
        return None
