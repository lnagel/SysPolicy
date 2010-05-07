
import syspolicy.change
from syspolicy.change import Change, ChangeSet
from syspolicy.modules.module import Module
import re

class Quota(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "quota"
        self.handled_attributes['groups'] = ['userquota', 'groupquota']
    
    def pol_set_attribute(self, group, attribute, value):
        print "Setting attribute value in the Quota module", attribute, "=", value
        for partition, quota in value.items():
            print "Quota for", partition, "set to", kilobytes(quota), "kilobytes"
        return ChangeSet(Change(self.name, "set_attribute", {'group': group, 'attribute': attribute, 'value': value}))


def kilobytes(sizestr):
    if isinstance(sizestr, str):
        powers = {'k': 1, 'm': 1024, 'g': 1024*1024, 't': 1024*1024*1024}
        m = re.match('^([0-9]*)([kmgt]?)$', sizestr.lower())
        if m and m.group(2) in powers:
            return int(m.group(1)) * powers[m.group(2)]
    return 0
