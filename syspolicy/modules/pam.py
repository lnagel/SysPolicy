
import syspolicy.change
from syspolicy.change import Change, ChangeSet
from syspolicy.modules.module import Module

class PAM(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "pam"
        self.handled_attributes['services'] = ['groups_allow',  'groups_deny',  'users_allow',  'users_deny']
        self.change_operations['set_default'] = self.set_default
    
    def pol_set_default(self, attribute,  value):
        print "Setting new default in the PAM module", attribute, "=", value
        return ChangeSet(Change("shadow", "set_default", {attribute: value}))
    
    def pol_set_attribute(self, group, attribute, value):
        print "Setting attribute value in the PAM module", attribute, "=", value
        return ChangeSet(Change(self.name, "set_attribute", {'group': group, attribute: value}))

    def set_default(self, change):
        return syspolicy.change.STATE_COMPLETED
