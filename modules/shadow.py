
import pwd,  grp
from module import Module

class Shadow(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "shadow"
        self.handled_attributes['groups'] = ['uid_min',  'uid_max',  'usergroups',  'grouphomes',  'basedir']
    
    def list_groups(self):
        return grp.getgrall()
