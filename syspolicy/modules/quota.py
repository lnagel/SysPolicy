
import syspolicy.change
from syspolicy.change import Change, ChangeSet
import syspolicy.event
from syspolicy.modules.module import Module
import syspolicy.modules.shadow as shadow
import re

SETQUOTA = "/usr/sbin/setquota"

class Quota(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "quota"
        self.handled_attributes['groups'] = ['userquota', 'groupquota']
        self.change_operations['set_quota'] = self.set_quota
        self.event_hooks[syspolicy.event.USER_ADDED] = self.handle_event
        self.event_hooks[syspolicy.event.USER_MODIFIED] = self.handle_event
        self.event_hooks[syspolicy.event.USER_REMOVED] = self.handle_event
    
    def cs_rem_attribute(self, group, attribute, value, diff):
        if attribute in self.handled_attributes['groups']:
            return self.cs_set_attribute(group, attribute, {}, diff)
    
    def cs_set_attribute(self, group, attribute, value, diff):
        cs = ChangeSet()
        if attribute == 'groupquota':
            cs.extend(self.c_set_quota(diff, 'group', group))
        elif attribute == 'userquota':
            gid = shadow.get_group_by_name(group).gr_gid
            for user in shadow.list_users_with_gid(gid):
                cs.extend(self.c_set_quota(diff, 'user', user.pw_name))
        return cs
    
    def c_set_quota(self, quota, type, object):
        changes = []
        for fs, limit in quota.items():
            c = Change(self.name, "set_quota",
                    {'type': type, 'object': object,
                     'block-hardlimit': kilobytes(limit), 'filesystem': fs})
            changes.append(c)
        return changes
    
    def handle_event(self, event, changeset):
        print "Quota module caught event", event, "with changeset", changeset
        for change in changeset.changes:
            if change.operation == 'add_user':
                group = change.parameters['group']
                userquota = self.pt.policy['groups'].get([group, 'userquota'])
                changeset.extend(self.c_set_quota(userquota, 'user', change.parameters['username']))
    
    def set_quota(self, change):
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


def kilobytes(sizestr):
    if isinstance(sizestr, str):
        units = {'k': 1, 'm': 1024, 'g': 1024*1024, 't': 1024*1024*1024}
        m = re.match('^([0-9]*)([kmgt]?)$', sizestr.lower())
        if m and m.group(2) in units:
            return int(m.group(1)) * units[m.group(2)]
    return 0
