
import pwd, grp
import syspolicy.change
from syspolicy.change import Change, ChangeSet
from syspolicy.modules.module import Module

class Shadow(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "shadow"
        self.handled_attributes['groups'] = ['uid_min', 'uid_max',
                'usergroups', 'grouphomes', 'basedir',
                'shell', 'skeleton', 'expire', 'inactive']
        self.change_operations['set_default'] = self.set_default
    
    def pol_set_default(self, attribute, value, diff):
        print "Setting new default in the Shadow module", attribute, "=", value
        return ChangeSet(Change("shadow", "set_default", {attribute: value}))
    
    def pol_set_attribute(self, group, attribute, value, diff):
        print "Setting attribute value in the Shadow module", attribute, "=", value
        return ChangeSet(Change(self.name, "set_attribute", {'group': group, 'attribute': attribute, 'value': value}))

    def set_default(self, change):
        return syspolicy.change.STATE_COMPLETED

    
def list_groups():
    return grp.getgrall()

def list_users():
    return pwd.getpwall()

def get_group_by_name(name):
    return grp.getgrnam(name)

def list_users_with_gid(gid):
    users = []
    for u in list_users():
        if u.pw_gid == gid:
            users.append(u)
    return users
