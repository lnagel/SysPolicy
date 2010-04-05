
import pwd,  grp
import syspolicy.core.change
from syspolicy.core.change import Change, ChangeSet
from syspolicy.modules.module import Module

class Shadow(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "shadow"
        self.handled_attributes['groups'] = ['uid_min',  'uid_max',  'usergroups',  'grouphomes',  'basedir']
        self.change_operations['set_default'] = self.set_default
    
    def list_groups(self):
        return grp.getgrall()
    
    def pol_set_default(self, attribute,  value):
        print "Setting new default in the Shadow module", attribute, "=", value
        return ChangeSet(Change("shadow", "set_default", {attribute: value}))
    
    def pol_set_attribute(self, group, attribute, value):
        print "Setting attribute value in the Shadow module", attribute, "=", value
        return ChangeSet(Change(self.name, "set_attribute", {'group': group, attribute: value}))

    def set_default(self, change):
        return syspolicy.core.change.STATE_COMPLETED