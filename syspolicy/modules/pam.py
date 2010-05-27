# SysPolicy
# 
# Copyright (c) 2010 Lenno Nagel
# Author: Lenno Nagel <lenno-at-nagel.ee>
# URL: <http://trac.syspolicy.org>
# Released under the GNU General Public License version 3

import os
import syspolicy.change
from syspolicy.change import Change, ChangeSet
from syspolicy.modules.module import Module

class PAM(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "pam"
        self.handled_attributes['services'] = ['groups_allow', 'groups_deny',
                'users_allow', 'users_deny', 'password']
    
    def cs_rem_attribute(self, group, attribute, value, diff):
        if attribute in self.handled_attributes['services']:
            return self.cs_set_attribute(group, attribute, [], diff)
    
    def cs_set_attribute(self, group, attribute, value, diff):
        configfile = self.pt.conf.get(['module-pam', 'pam-dir']) + '/' + group
        lines = []
        
        if not os.access(configfile, os.F_OK):
            raise Exception("PAM service config file '" + configfile + "' does not exist")
        
        # TODO: Make this function work with more than one group per attribute
        if attribute in ['groups_allow'] and len(value) > 1:
            raise Exception("Cannot handle more than 1 group in the attribute " + attribute + " yet")
        
        before = '^account'
        after = None
        
        if attribute == 'groups_allow':
            for group in value:
                lines.append('account required pam_succeed_if.so user ingroup ' + group)
        elif attribute == 'groups_deny':
            for group in value:
                lines.append('account required pam_succeed_if.so user notingroup ' + group)
        elif attribute == 'users_allow':
            if len(value) == 1:
                lines.append('account required pam_succeed_if.so user = ' + value[0])
            elif len(value) > 1:
                lines.append('account required pam_succeed_if.so user in ' + ':'.join(value))
        elif attribute == 'users_deny':
            if len(value) == 1:
                lines.append('account required pam_succeed_if.so user != ' + value[0])
            elif len(value) > 1:
                lines.append('account required pam_succeed_if.so user notin ' + ':'.join(value))
        elif attribute == 'password':
            args = []
            before = '^password(.*)pam_unix.so'
            for k, v in value.items():
                if k in ['retry', 'difok', 'difignore', 'minlen',
                        'dcredit', 'ucredit', 'lcredit', 'ocredit',
                        'minclass', 'maxrepeat']:
                    if type(v) == int:
                        args.append(k + '=' + str(v))
                    elif type(v) == None:
                        pass
                    else:
                        raise Exception('Argument '+k+' should have an integer value')
                else:
                    raise Exception('Argument ' + str(k) +
                            ' is not supported by pam_cracklib.so')
            if len(args) > 0:
                lines.append('password required pam_cracklib.so ' + ' '.join(args))
        
        params = {}
        params['configfile'] = configfile
        params['before'] = before
        params['after'] = after
        params['id'] = attribute
        params['lines'] = lines

        return ChangeSet(Change(self.name, "edit_configfile", params))
