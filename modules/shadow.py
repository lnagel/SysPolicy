
import pwd,  grp
from module import Module
from core.change import Change, ChangeSet

class Shadow(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "shadow"
        self.handled_attributes['groups'] = ['uid_min',  'uid_max',  'usergroups',  'grouphomes',  'basedir']
    
    def list_groups(self):
        return grp.getgrall()
    
    def pol_set_default(self, attribute,  value):
        print "Setting new default in the Shadow module", attribute, "=", value
        cs = ChangeSet()
        cs.append(Change("shadow", "set_default", {attribute: value}))
        return cs
