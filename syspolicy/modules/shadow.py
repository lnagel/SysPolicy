
import pwd, grp
import copy
from datetime import date, timedelta
import syspolicy.change
import syspolicy.event
from syspolicy.change import Change, ChangeSet
from syspolicy.policy import merge_into
from syspolicy.modules.module import Module

USERADD = '/usr/sbin/useradd'

class Shadow(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "shadow"
        self.handled_attributes['groups'] = ['uid_min', 'uid_max',
                'usergroups', 'grouphomes', 'basedir', 'create_homedir', 
                'shell', 'skeleton', 'expire', 'inactive']
        self.change_operations['add_user'] = self.add_user
    
    def cs_set_attribute(self, group, attribute, value, diff):
        print "Setting attribute value in the Shadow module", attribute, "=", value
        return ChangeSet(Change(self.name, "set_attribute", {'group': group, 'attribute': attribute, 'value': value}))
    
    def cs_add_user(self, username, group, extragroups=[],
                    name=None, homedir=None, policy={}):
        
        upolicy = copy.deepcopy(self.pt.policy['groups'].get([group]))
        args = {'username': username, 'group': group, 'name': name,
                'extragroups': extragroups, 'homedir': homedir}
        
        upolicy = merge_into(upolicy, policy)
        args = merge_into(upolicy, args)
        
        if args['grouphomes'] == True:
            args['basedir'] = args['basedir'] + '/' + args['group']
        if args['name'] is None:
            args['name'] = ''
        if args['homedir'] is None:
            args['homedir'] = args['basedir'] + '/' + args['username']
        
        cs = ChangeSet(Change(self.name, "add_user", args))
        self.pt.emit_event(syspolicy.event.USER_ADDED, cs)
        return cs
    
    def add_user(self, change):        
        cmd = [USERADD]
        
        cmd.extend(['--comment', change.parameters['name']])
        cmd.extend(['--home-dir', change.parameters['homedir']])
        if change.parameters['expire'] > 0:
            expiredate = date.today() + timedelta(change.parameters['expire'])
            cmd.extend(['--expiredate', expiredate.isoformat()])
        cmd.extend(['--inactive', str(change.parameters['inactive'])])
        cmd.extend(['--gid', change.parameters['group']])
        if change.parameters['extragroups']:
            cmd.extend(['--groups', ','.join(change.parameters['extragroups'])])
        cmd.extend(['--skel', change.parameters['skeleton']])
        cmd.extend(['--key', 'UID_MIN=' + str(change.parameters['uid_min'])])
        cmd.extend(['--key', 'UID_MAX=' + str(change.parameters['uid_max'])])
        if change.parameters['create_homedir']:
            cmd.append('--create-home')
        if change.parameters['usergroups']:
            cmd.append('--user-group')
        else:
            cmd.append('--no-user-group')
        # --password
        cmd.extend(['--shell', change.parameters['shell']])
        
        cmd.append(change.parameters['username'])
        
        return self.execute(cmd)

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
