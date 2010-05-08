
import syspolicy.change
from syspolicy.change import Change, ChangeSet
import syspolicy.event
from syspolicy.modules.module import Module
import syspolicy.modules.shadow as shadow
import re
import subprocess

SETQUOTA = "/usr/sbin/setquota"

class Quota(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "quota"
        self.handled_attributes['groups'] = ['userquota', 'groupquota']
        self.change_operations['set_quota'] = self.set_quota
        self.event_hooks.append(syspolicy.event.USER_ADDED)
        self.event_hooks.append(syspolicy.event.USER_MODIFIED)
        self.event_hooks.append(syspolicy.event.USER_REMOVED)
    
    def cs_rem_attribute(self, group, attribute, value, diff):
        if attribute in self.handled_attributes['groups']:
            return self.cs_set_attribute(group, attribute, {}, diff)
    
    def cs_set_attribute(self, group, attribute, value, diff):
        cs = ChangeSet()
        if attribute == 'groupquota':
            for fs, quota in diff.items():
                c = Change(self.name, "set_quota",
                        {'type': 'group', 'object': group,
                            'block-hardlimit': kilobytes(quota), 'filesystem': fs})
                cs.append(c)
        elif attribute == 'userquota':
            gid = shadow.get_group_by_name(group).gr_gid
            for user in shadow.list_users_with_gid(gid):
                for fs, quota in diff.items():
                    c = Change(self.name, "set_quota",
                            {'type': 'user', 'object': user.pw_name,
                                'block-hardlimit': kilobytes(quota), 'filesystem': fs})
                    cs.append(c)
        return cs
    
    def set_quota(self, change):
        # /usr/sbin/setquota [-u|-g] [-F quotaformat] <user|group>
        # <block-softlimit> <block-hardlimit> <inode-softlimit> <inode-hardlimit> -a|<filesystem>
        types = {'user': '-u', 'group': '-g'}
        cmd = []
        
        cmd.append(SETQUOTA)
        cmd.append(types[change.parameters['type']])            
        cmd.append(change.parameters['object'])
        cmd.append(str(change.parameters.get('block-softlimit', 0)))
        cmd.append(str(change.parameters.get('block-hardlimit', 0)))
        cmd.append(str(change.parameters.get('inode-softlimit', 0)))
        cmd.append(str(change.parameters.get('inode-hardlimit', 0)))
        cmd.append(change.parameters['filesystem'])
        
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        p.wait()
        
        if stderr:
            raise Exception(stderr)
        elif p.returncode == 0:
            return syspolicy.change.STATE_COMPLETED
        else:
            return syspolicy.change.STATE_FAILED


def kilobytes(sizestr):
    if isinstance(sizestr, str):
        units = {'k': 1, 'm': 1024, 'g': 1024*1024, 't': 1024*1024*1024}
        m = re.match('^([0-9]*)([kmgt]?)$', sizestr.lower())
        if m and m.group(2) in units:
            return int(m.group(1)) * units[m.group(2)]
    return 0