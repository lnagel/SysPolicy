
import pwd, grp
import copy
from datetime import date, timedelta
import syspolicy.change
import syspolicy.event
from syspolicy.change import Change, ChangeSet
from syspolicy.policy import merge_into
from syspolicy.modules.module import Module

USERADD = '/usr/sbin/useradd'
USERMOD = '/usr/sbin/usermod'
USERDEL = '/usr/sbin/userdel'
GROUPADD = '/usr/sbin/groupadd'
GROUPDEL = '/usr/sbin/groupdel'

class Shadow(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "shadow"
        self.handled_attributes['groups'] = ['uid_min', 'uid_max',
                'usergroups', 'grouphomes', 'basedir', 'create_homedir', 
                'shell', 'skeleton', 'expire', 'inactive']
        self.change_operations['add_user'] = self.add_user
        self.change_operations['mod_user'] = self.mod_user
        self.change_operations['del_user'] = self.del_user
        self.change_operations['add_group'] = self.add_group
        self.change_operations['del_group'] = self.del_group
    
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
    
    def cs_mod_user(self, username, group=None, extragroups=[],
                    name=None, homedir=None, policy={}):
        # retrieve information about the users current group
        oldgid = get_user_by_name(username).pw_gid
        oldgroup = get_group_by_id(oldgid).gr_name
        
        args = {'username': username}
        args = merge_into(args, policy)
        
        if group is not None:
            args['group'] = group
            args['oldgroup'] = oldgroup
            args['extragroups'] = extragroups
        if name is not None:
            args['name'] = name
        if homedir is not None:
            args['homedir'] = homedir
        
        cs = ChangeSet(Change(self.name, "mod_user", args))
        self.pt.emit_event(syspolicy.event.USER_MODIFIED, cs)
        return cs
    
    def cs_del_user(self, username):
        # retrieve information about the users current group
        gid = get_user_by_name(username).pw_gid
        group = get_group_by_id(gid).gr_name
        
        args = {'username': username, 'group': group}
        
        cs = ChangeSet(Change(self.name, "del_user", args))
        self.pt.emit_event(syspolicy.event.USER_REMOVED, cs)
        return cs
    
    def cs_add_group(self, group):
        cs = ChangeSet(Change(self.name, "add_group", {'group': group}))
        self.pt.emit_event(syspolicy.event.GROUP_ADDED, cs)
        return cs
    
    def cs_del_group(self, group):
        cs = ChangeSet(Change(self.name, "del_group", {'group': group}))
        self.pt.emit_event(syspolicy.event.GROUP_REMOVED, cs)
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
        if 'password' in p:
            cmd.extend(['--password', p['password']])
        cmd.extend(['--shell', p['shell']])
        
        cmd.append(p['username'])
        
        return self.execute(cmd)
    
    def mod_user(self, change):
        p = change.parameters
        cmd = [USERMOD]
        
        if 'name' in p:
            cmd.extend(['--comment', p['name']])
        if 'homedir' in p:
            cmd.extend(['--home', p['homedir']])
        if 'expire' in p and p['expire'] > 0:
            expiredate = date.today() + timedelta(p['expire'])
            cmd.extend(['--expiredate', expiredate.isoformat()])
        if 'inactive' in p:
            cmd.extend(['--inactive', str(p['inactive'])])
        if 'group' in p:
            cmd.extend(['--gid', p['group']])
        if 'extragroups' in p and p['extragroups']:
            cmd.extend(['--groups', ','.join(p['extragroups'])])
        # --append ?
        # --move-home
        if 'password' in p:
            cmd.extend(['--password', p['password']])
        if 'shell' in p:
            cmd.extend(['--shell', p['shell']])
        
        cmd.append(p['username'])
        
        return self.execute(cmd)
    
    def del_user(self, change):
        p = change.parameters
        cmd = [USERDEL]
        cmd.append(p['username'])
        
        return self.execute(cmd)
    
    def add_group(self, change):
        p = change.parameters
        cmd = [GROUPADD]
        cmd.append(p['group'])
        
        return self.execute(cmd)
    
    def del_group(self, change):
        cmd = [GROUPDEL, change.parameters['group']]
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
