# SysPolicy
# 
# Copyright (c) 2010 Lenno Nagel
# Author: Lenno Nagel <lenno-at-nagel.ee>
# URL: <http://trac.syspolicy.org>
# Released under the GNU General Public License version 3

"""
Shadow users/passwords configuration support
"""

import pwd, grp
import copy
import datetime
import syspolicy.change
import syspolicy.event
from syspolicy.change import Change, ChangeSet
from syspolicy.config import compare_trees
from syspolicy.policy import merge_into
from syspolicy.modules.module import Module

USERADD = '/usr/sbin/useradd'
USERMOD = '/usr/sbin/usermod'
USERDEL = '/usr/sbin/userdel'
GROUPADD = '/usr/sbin/groupadd'
GROUPDEL = '/usr/sbin/groupdel'

class Shadow(Module):
    """
    This module provides shadow users & groups management support for SysPolicy.
    
    The features include full add, modify and remove operations and all
    the attributes supported by the standard utilities are supported. These
    include specifying the basedir, homedir, grouping of home directories,
    real name of the user, account expiration and inactivity periods, groups,
    custom skeleton directories, assigning specific shells and password
    auto-generation combined with strength checking.
    """
    def __init__(self):
        Module.__init__(self)
        self.name = "shadow"
        self.handled_attributes['groups'] = ['shell', 'inactive']
        self.change_operations['add_user'] = self.add_user
        self.change_operations['mod_user'] = self.mod_user
        self.change_operations['del_user'] = self.del_user
        self.change_operations['add_group'] = self.add_group
        self.change_operations['del_group'] = self.del_group
    
    def cs_set_attribute(self, group, attribute, value, diff):
        """
        This function returns a ChangeSet respective to a changed policy attribute.
        
        In case the changed attribute affects existing users, the group
        members' accounts will be updated as well. For example, when
        the shell of the group was changed, you probably want all the accounts
        to be updated.
        """
        cs = ChangeSet()
        p = {attribute: value}
        
        # check if we need to update group members
        if attribute in ['shell', 'inactive'] and group_exists(group):
            gid = get_group_by_name(group).gr_gid
            for user in list_users_with_gid(gid):
                # modify each user in the group
                cs.merge(self.cs_mod_user(user.pw_name, policy=p))
        return cs
    
    def cs_add_user(self, username, group, password, extragroups=[],
                    name=None, homedir=None, policy={}):
        """
        This function returns a ChangeSet for when a new user account
        needs to be created. It prepares the arguments that need to be
        passed to the useradd utility based on the arguments given and
        the users' group policy.
        
        @param username: The username of the new account
        @param group: The primary group name
        @param password: The password for the account in crypt hash format
        @param extragroups: Extra groups that the new account should belong to
        @param name: Real name of the accont owner
        @param homedir: Custom home directory for this account
        @param policy: Additional parameters that override the group policy
        @return: A ChangeSet
        """
        # create a copy of the group policy so it can be safely edited
        upolicy = copy.deepcopy(self.pt.policy['groups'].get([group]))
        # place the given arguments into a policy dictionary
        args = {'username': username, 'group': group, 'name': name,
                'extragroups': extragroups, 'homedir': homedir, 'password': password}
        
        # overlay the group policy with any values specified by the user
        upolicy = merge_into(upolicy, policy)
        # overlay the policy with the arguments (username, password, ..)
        args = merge_into(upolicy, args)
        
        # construct the final home directory path
        if args['grouphomes'] == True:
            args['basedir'] = args['basedir'] + '/' + args['group']
        if args['name'] is None:
            args['name'] = ''
        if args['homedir'] is None:
            args['homedir'] = args['basedir'] + '/' + args['username']
        
        # prepare the ChangeSet
        cs = ChangeSet(Change(self.name, "add_user", args))
        # notify the PolicyTool with a USER_ADDED event
        self.pt.emit_event(syspolicy.event.USER_ADDED, cs)
        
        return cs
    
    def cs_mod_user(self, username, group=None, extragroups=[],
                    password=None, name=None, homedir=None, policy={}):
        """
        This function returns a ChangeSet which performs user modification.
        
        It prepares any given arguments and checks also if changing the 
        primary group was requested. In case the primary group is to be
        changed, the function also includes the differences from the old
        to the new group policy, keeping the account up to date (eg. quota).
        
        @param username: The username of the account to be modified
        @param group: The new primary group name
        @param password: The new password for the account in crypt hash format
        @param extragroups: Extra groups that the new account should belong to
        @param name: Real name of the accont owner
        @param homedir: Custom home directory for this account
        @param policy: Additional parameters that override the group policy
        @return: A ChangeSet
        """
        # retrieve information about the users current group
        oldgid = get_user_by_name(username).pw_gid
        oldgroup = get_group_by_id(oldgid).gr_name
        
        # merge the given arguments into dict args
        args = {'username': username}
        args = merge_into(args, policy)
        
        # if changing the primary group
        if group is not None:
            args['group'] = group
            args['oldgroup'] = oldgroup
            args['extragroups'] = extragroups
            
            # find out the differences between the old and the new policy
            npol = self.pt.policy['groups'].get([group])
            opol = self.pt.policy['groups'].get([oldgroup])
            diff = compare_trees(npol, opol)
            
            # merge in the attributes that have new values
            for attr in diff:
                args[attr] = diff[attr]
        if password is not None:
            args['password'] = password
        if name is not None:
            args['name'] = name
        if homedir is not None:
            args['homedir'] = homedir
        
        # prepare the ChangeSet
        cs = ChangeSet(Change(self.name, "mod_user", args))
        # notify the PolicyTool with a USER_MODIFIED event
        self.pt.emit_event(syspolicy.event.USER_MODIFIED, cs)
        return cs
    
    def cs_del_user(self, username):
        """
        This function returns a ChangeSet which performs user removal.
        
        @param username: The user account to be removed.
        @return: A ChangeSet
        """
        # retrieve information about the users current group
        gid = get_user_by_name(username).pw_gid
        group = get_group_by_id(gid).gr_name
        gpolicy = copy.deepcopy(self.pt.policy['groups'].get([group]))
        
        # prepare the arguments
        args = {'username': username, 'group': group}
        args = merge_into(gpolicy, args)
        
        # prepare the ChangeSet
        cs = ChangeSet(Change(self.name, "del_user", args))
        # notify the PolicyTool with a USER_REMOVED event
        self.pt.emit_event(syspolicy.event.USER_REMOVED, cs)
        return cs
    
    def cs_add_group(self, group):
        """
        This function returns a ChangeSet which adds a new group.
        
        @param group: The name of the new group
        @return: A ChangeSet
        """
        cs = ChangeSet(Change(self.name, "add_group", {'group': group}))
        # notify the PolicyTool with a GROUP_ADDED event
        self.pt.emit_event(syspolicy.event.GROUP_ADDED, cs)
        return cs
    
    def cs_del_group(self, group):
        """
        This function returns a ChangeSet which removes a group.
        
        @param group: The name of the group to be removed
        @return: A ChangeSet
        """
        cs = ChangeSet(Change(self.name, "del_group", {'group': group}))
        # notify the PolicyTool with a GROUP_REMOVED event
        self.pt.emit_event(syspolicy.event.GROUP_REMOVED, cs)
        return cs
    
    def add_user(self, change):
        """
        This function performs user addition by executing the useradd command.
        
        @param change: Change element with parameters
        @return: STATE_COMPLETED or STATE_FAILED
        """
        p = change.parameters
        cmd = [USERADD]
        
        # build the command line arguments list for useradd
        if p['name']:
            cmd.extend(['--comment', p['name']])
        cmd.extend(['--home-dir', p['homedir']])
        if p['expire'] > 0:
            expiredate = datetime.date.today() + datetime.timedelta(p['expire'])
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
        else:
            cmd.append('--no-user-group')
        if 'password' in p and p['password'] is not None:
            cmd.extend(['--password', p['password']])
        cmd.extend(['--shell', p['shell']])
        
        # append the username as the last attribute
        cmd.append(p['username'])
        
        # execute the command and return the return value
        return self.execute(cmd)
    
    def mod_user(self, change):
        """
        This function performs user modification by executing the usermod command.
        
        @param change: Change element with parameters
        @return: STATE_COMPLETED or STATE_FAILED
        """
        p = change.parameters
        cmd = [USERMOD]
        
        # build the command line arguments list for usermod
        # only include the values that have been set
        if 'name' in p:
            cmd.extend(['--comment', p['name']])
        if 'homedir' in p:
            cmd.extend(['--home', p['homedir']])
        if 'expire' in p and p['expire'] > 0:
            expiredate = datetime.date.today() + datetime.timedelta(p['expire'])
            cmd.extend(['--expiredate', expiredate.isoformat()])
        if 'inactive' in p:
            cmd.extend(['--inactive', str(p['inactive'])])
        if 'group' in p:
            cmd.extend(['--gid', p['group']])
        if 'extragroups' in p and p['extragroups']:
            cmd.extend(['--groups', ','.join(p['extragroups'])])
        # --append ?
        # --move-home
        if 'password' in p and p['password'] is not None:
            cmd.extend(['--password', p['password']])
        if 'shell' in p:
            cmd.extend(['--shell', p['shell']])
        
        # append the username as the last attribute
        cmd.append(p['username'])
        
        # execute the command and return the return value
        return self.execute(cmd)
    
    def del_user(self, change):
        """
        This function performs user deletion by executing the userdel command.
        
        @param change: Change element with parameters
        @return: STATE_COMPLETED or STATE_FAILED
        """
        p = change.parameters
        cmd = [USERDEL]
        
        # append the username as the only attribute
        cmd.append(p['username'])
        
        # execute the command and return the return value
        return self.execute(cmd)
    
    def add_group(self, change):
        """
        This function performs group addition by executing the groupadd command.
        
        @param change: Change element with parameters
        @return: STATE_COMPLETED or STATE_FAILED
        """
        # prepare the command
        cmd = [GROUPADD, change.parameters['group']]
        
        # execute the command and return the return value
        return self.execute(cmd)
    
    def del_group(self, change):
        """
        This function performs group deletion by executing the groupdel command.
        
        @param change: Change element with parameters
        @return: STATE_COMPLETED or STATE_FAILED
        """
        # prepare the command
        cmd = [GROUPDEL, change.parameters['group']]
        
        # execute the command and return the return value
        return self.execute(cmd)
    
    def get_password_policy(self):
        """
        This module returns the system main password security policy by looking
        it up from the main configuration and the service policy.
        
        @return: A dictionary with password policy (cracklib-style keys-values)
        """
        # find out in which service group is the main password policy
        svcgroup = self.pt.conf.get(['module-pam', 'password'])
        
        # if there is no main policy defined, return an empty policy
        if svcgroup is None:
            return {}
        
        # attempt to get the password policy from the specified service group
        policy = self.pt.policy['services'].get([svcgroup, 'password'])
        if policy is None:
            return {}
        
        # if the policy exists, return it
        return policy


def list_groups():
    """
    This function lists all the groups in the system.
    
    @return: List of existing groups
    """
    return grp.getgrall()

def list_users():
    """
    This function lists all the users in the system.
    
    @return: List of existing users
    """
    return pwd.getpwall()

def get_group_by_id(id):
    """
    This function gets a group by it's GID.
    
    @return: Shadow group with the GID `id`
    """
    return grp.getgrgid(id)

def get_group_by_name(name):
    """
    This function gets a group by it's name.
    
    @return: Shadow group with the name `name`
    """
    return grp.getgrnam(name)

def group_exists(name):
    """
    This function checks if a group with the name `name` exists.
    
    @return: True if the grup exists, False otherwise
    """
    return grp.getgrnam(name) is not None

def get_user_by_name(name):
    """
    This function gets a user by it's name.
    
    @return: Shadow user with the name `name`
    """
    return pwd.getpwnam(name)

def list_users_with_gid(gid):
    """
    This function lists users with the primary group id `gid`
    
    @return: List of shadow users
    """
    users = []
    for u in list_users():
        if u.pw_gid == gid:
            users.append(u)
    return users
