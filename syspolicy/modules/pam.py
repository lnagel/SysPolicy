# SysPolicy
# 
# Copyright (c) 2010 Lenno Nagel
# Author: Lenno Nagel <lenno-at-nagel.ee>
# URL: <http://trac.syspolicy.org>
# Released under the GNU General Public License version 3

"""
PAM configuration support
"""

import os
import syspolicy.change
from syspolicy.change import Change, ChangeSet
from syspolicy.modules.module import Module

class PAM(Module):
    """
    This module provides PAM configuration support for SysPolicy.
    """
    
    def __init__(self):
        Module.__init__(self)
        self.name = "pam"
        self.handled_attributes['services'] = ['groups_allow', 'groups_deny',
                'users_allow', 'users_deny', 'password']
    
    def cs_rem_attribute(self, group, attribute, value, diff):
        """
        This function produces a ChangeSet for removing an attribute.
        """
        if attribute in self.handled_attributes['services']:
            return self.cs_set_attribute(group, attribute, [], diff)
    
    def cs_set_attribute(self, group, attribute, value, diff):
        """
        This function produces a ChangeSet for setting a value in the
        services policy. It handles the user/group allow and deny attributes
        as well as the password strenght policy using pam_cracklib.so
        
        It will always return a ChangeSet which contains the exact lines
        that needed to be changed in a specific PAM configuration file.
        """
        configfile = self.pt.conf.get(['module-pam', 'pam-dir']) + '/' + group
        lines = []
        
        # attempt to access that configuration file
        if not os.access(configfile, os.F_OK):
            raise Exception("PAM service config file '" + configfile + "' does not exist")
        
        # TODO: Make this function work with more than one group per attribute
        if attribute in ['groups_allow'] and len(value) > 1:
            raise Exception("Cannot handle more than 1 group in the attribute " + attribute + " yet")
        
        before = '^account'
        after = None
        
        # depending on the attribute that is edited, produce the configuration
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
            
            # for all the attributes specified in the policy ..
            for k, v in value.items():
                # check if they are valid
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
        
        # set up the parameters for the edit_configfile Change operation
        params = {}
        params['configfile'] = configfile
        params['before'] = before
        params['after'] = after
        params['id'] = attribute
        params['lines'] = lines

        return ChangeSet(Change(self.name, "edit_configfile", params))
