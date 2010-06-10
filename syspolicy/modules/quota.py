# SysPolicy
# 
# Copyright (c) 2010 Lenno Nagel
# Author: Lenno Nagel <lenno-at-nagel.ee>
# URL: <http://trac.syspolicy.org>
# Released under the GNU General Public License version 3

"""
Quota configuration support
"""

import re
import copy
import syspolicy.change
import syspolicy.event
import syspolicy.modules.shadow as shadow
from syspolicy.change import Change, ChangeSet
from syspolicy.modules.module import Module
from syspolicy.config import compare_trees

SETQUOTA = "/usr/sbin/setquota"

class Quota(Module):
    """
    This module provides Linux quota configuration support for SysPolicy.
    """
    
    def __init__(self):
        Module.__init__(self)
        self.name = "quota"
        self.handled_attributes['groups'] = ['userquota', 'groupquota']
        self.change_operations['set_quota'] = self.set_quota
        self.event_hooks[syspolicy.event.USER_ADDED] = self.event_user_modified
        self.event_hooks[syspolicy.event.USER_MODIFIED] = self.event_user_modified
        self.event_hooks[syspolicy.event.USER_REMOVED] = self.event_user_removed
        self.event_hooks[syspolicy.event.GROUP_ADDED] = self.event_group_added
        self.event_hooks[syspolicy.event.GROUP_REMOVED] = self.event_group_removed
    
    def cs_rem_attribute(self, group, attribute, value, diff):
        if attribute in self.handled_attributes['groups']:
            return self.cs_set_attribute(group, attribute, {}, diff)
    
    def cs_set_attribute(self, group, attribute, value, diff):
        """
        This function returns a ChangeSet for setting user- and group quotas
        based on the policy. In case user quotas are being changed for the 
        group, it queries for all the members of the group and returns a Change
        element for setting the quota for each of them.
        """
        cs = ChangeSet()
        if attribute == 'groupquota':
            cs.extend(self.c_set_quota(diff, 'group', group))
        elif attribute == 'userquota':
            try:
                gid = shadow.get_group_by_name(group).gr_gid
                for user in shadow.list_users_with_gid(gid):
                    cs.extend(self.c_set_quota(diff, 'user', user.pw_name))
            except:
                pass
        return cs
    
    def c_set_quota(self, quota, type, object):
        """
        This function expands a dictionary of key-value pairs in the quota
        variable so that a separate Change operation is given for each key
        (a filesystem mount point) and value (amount of quota).
        
        @param quota: Dictionary of mountpoints and their quota
        @param type: Type of the quota being set ('user' or 'group')
        @param object: The name of the user or group for which quota is set
        @return: List of Change elements which set the quota
        """
        changes = []
        for fs, limits in quota.items():
            params = extract_quota(limits)
            params['type'] = type
            params['object'] = object
            params['filesystem'] = fs            
            c = Change(self.name, "set_quota", params)
            changes.append(c)
        return changes
    
    def event_user_modified(self, event, changeset):
        """
        This function catches user modification events and updates their
        quota accordingly if it's needed. Such changes in quota often
        come from changed main group.
        
        The function appends any Change elements to the provided ChangeSet.
        
        @param event: The event that was triggered
        @param changeset: The ChangeSet triggering the event
        """
        if self.pt.debug:
            print "Quota module caught event", event, "with changeset", changeset
        for change in changeset.changes:
            if change.operation in ['add_user', 'mod_user'] and 'userquota' in change.parameters:
                quota = change.parameters['userquota']
                changeset.extend(self.c_set_quota(quota, 'user', change.parameters['username']))
    
    def event_user_removed(self, event, changeset):
        """
        This function catches user removal events and removes their
        quota before the user is removed from the system.
        
        The function inserts any Change elements to the provided ChangeSet,
        before the actual user deletion Changes.
        
        @param event: The event that was triggered
        @param changeset: The ChangeSet triggering the event
        """
        if self.pt.debug:
            print "Quota module caught event", event, "with changeset", changeset
        changes = []
        for change in changeset.changes:
            if change.operation == 'del_user' and 'userquota' in change.parameters:            
                quota = copy.copy(change.parameters['userquota'])
                for fs in quota:
                    quota[fs] = 0
                changes.extend(self.c_set_quota(quota, 'user', change.parameters['username']))
        
        changes.reverse()
        for c in changes:
            changeset.insert(0, c)
    
    def event_group_added(self, event, changeset):
        """
        This function catches group addition events and sets their
        quota if it's needed.
        
        The function appends any Change elements to the provided ChangeSet.
        
        @param event: The event that was triggered
        @param changeset: The ChangeSet triggering the event
        """
        if self.pt.debug:
            print "Quota module caught event", event, "with changeset", changeset
        for change in changeset.changes:
            if change.operation in ['add_group'] and 'groupquota' in change.parameters:
                quota = change.parameters['groupquota']
                changeset.extend(self.c_set_quota(quota, 'group', change.parameters['group']))
    
    def event_group_removed(self, event, changeset):
        """
        This function catches group removal events and removes their
        quota before the group is removed from the system.
        
        The function inserts any Change elements to the provided ChangeSet,
        before the actual user deletion Changes.
        
        @param event: The event that was triggered
        @param changeset: The ChangeSet triggering the event
        """
        if self.pt.debug:
            print "Quota module caught event", event, "with changeset", changeset
        changes = []
        for change in changeset.changes:
            if change.operation == 'del_group' and 'groupquota' in change.parameters:            
                quota = copy.copy(change.parameters['groupquota'])
                for fs in quota:
                    quota[fs] = 0
                changes.extend(self.c_set_quota(quota, 'group', change.parameters['group']))
        
        changes.reverse()
        for c in changes:
            changeset.insert(0, c)
    
    def set_quota(self, change):
        """
        This function implements set_quota Changes by executing setquota
        according to the parameters which are given in the Change.
        
        @param change: The set_quota Change element
        @return: The return value from self.execute(cmd)
        """
        # /usr/sbin/setquota [-u|-g] [-F quotaformat] <user|group>
        # <block-softlimit> <block-hardlimit> <inode-softlimit> <inode-hardlimit> -a|<filesystem>
        p = change.parameters
        types = {'user': '-u', 'group': '-g'}
        cmd = [SETQUOTA]
        
        cmd.append(types[p['type']])            
        cmd.append(p['object'])
        cmd.append(str(p.get('block-softlimit', 0)))
        cmd.append(str(p.get('block-hardlimit', 0)))
        cmd.append(str(p.get('inode-softlimit', 0)))
        cmd.append(str(p.get('inode-hardlimit', 0)))
        cmd.append(p['filesystem'])
        
        return self.execute(cmd)

def extract_quota(limits):
    """
    This function extracts the quota definition from either a string or a list
    and returns a dictionary of detected values, which are directly suitable
    for passing on to the set_quota operation.
    
    Detected quita formats (given in YAML syntax):
    1) 256M - hard block size limit is set to 256M
    2) [256M] - hard block size limit is set to 256M
    3) [128M, 256M] - soft block limit 128M, hard limit 256M
    4) [128M, 256M, 2000, 4000] - soft block limit 128M, hard limit 256M,
        soft inode limit 2000, hard limit 4000
    
    @param limits: The limits' definition (string or list of strings)
    @return: Dictionary of detected values
    """
    quota = {}
    if isinstance(limits, str):
        quota['block-hardlimit'] = kilobytes(limits)
    elif type(limits) is list:
        if len(limits) == 1:
            quota['block-hardlimit'] = kilobytes(limits[0])
        elif len(limits) == 2:
            quota['block-softlimit'] = kilobytes(limits[0])
            quota['block-hardlimit'] = kilobytes(limits[1])
        elif len(limits) == 4:
            quota['block-softlimit'] = kilobytes(limits[0])
            quota['block-hardlimit'] = kilobytes(limits[1])
            quota['inode-softlimit'] = int(limits[2])
            quota['inode-hardlimit'] = int(limits[3])
    return quota

def kilobytes(sizestr):
    """
    This function converts a text-based size specification to kilobytes.
    The following units are accepted: K, M, G & T.
    
    @param sizestr: The size string containing an integer with a unit character
    @return: Integer value in kilobytes
    """
    if isinstance(sizestr, str):
        units = {'k': 1, 'm': 1024, 'g': 1024*1024, 't': 1024*1024*1024}
        m = re.match('^([0-9]*)([kmgt]?)$', sizestr.lower())
        if m and m.group(2) in units:
            return int(m.group(1)) * units[m.group(2)]
    return 0
