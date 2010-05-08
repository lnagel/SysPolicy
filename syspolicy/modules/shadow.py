
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
    
    def cs_mod_user(self, username, group, oldgroup, extragroups=[],
                    name=None, homedir=None, policy={}):
        
        args = {'username': username, 'group': group, 'name': name,
                'oldgroup': oldgroup, 'extragroups': extragroups,
                'homedir': homedir}
        
        cs = ChangeSet(Change(self.name, "mod_user", args))
        self.pt.emit_event(syspolicy.event.USER_MODIFIED, cs)
        return cs
    
    def add_user(self, change):
        p = change.parameters
        cmd = [USERADD]
        
        cmd.extend(['--comment', p['name']])
        cmd.extend(['--home-dir', p['homedir']])
        if p['expire'] > 0:
            expiredate = date.today() + timedelta(p['expire'])
            cmd.extend(['--expiredate', expiredate.isoformat()])
        cmd.extend(['--inactive', str(p['inactive'])])
        cmd.extend(['--gid', p['group']])
        if p['extragroups']:
            cmd.extend(['--groups', ','.join(p['extragroups'])])
        cmd.extend(['--skel', p['skeleton']])
        cmd.extend(['--key', 'UID_MIN=' + str(p['uid_min'])])
        cmd.extend(['--key', 'UID_MAX=' + str(p['uid_max'])])
        if p['create_homedir']:
            cmd.append('--create-home')
        if p['usergroups']:
            cmd.append('--user-group')
        else:
            cmd.append('--no-user-group')
        # --password
        cmd.extend(['--shell', p['shell']])
        
        cmd.append(p['username'])
        
        return self.execute(cmd)

    
def list_groups():
    return grp.getgrall()

def list_users():
    return pwd.getpwall()

def get_group_by_id(name):
    return grp.getgrgid(name)

def get_group_by_name(name):
    return grp.getgrnam(name)

def get_user_by_name(name):
    return pwd.getpwnam(name)

def list_users_with_gid(gid):
    users = []
    for u in list_users():
        if u.pw_gid == gid:
            users.append(u)
    return users
