
import syspolicy.change
from syspolicy.change import Change, ChangeSet
from syspolicy.modules.module import Module

class Quota(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "quota"
        self.handled_attributes['groups'] = ['userquota', 'groupquota']
    
    def pol_set_attribute(self, group, attribute, value):
        print "Setting attribute value in the Quota module", attribute, "=", value
        return ChangeSet(Change(self.name, "set_attribute", {'group': group, 'attribute': attribute, 'value': value}))
