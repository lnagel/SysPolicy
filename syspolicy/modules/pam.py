
import syspolicy.change
from syspolicy.change import Change, ChangeSet
from syspolicy.modules.module import Module
import os

class PAM(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "pam"
        self.handled_attributes['services'] = ['groups_allow', 'groups_deny',
                'users_allow', 'users_deny', 'password']
        self.change_operations['set_attribute'] = self.set_attribute
    
    def pol_set_attribute(self, group, attribute, value):
        print "Setting attribute value in the PAM module", attribute, "=", value
        return ChangeSet(Change(self.name, "set_attribute", {'group': group, 'attribute': attribute, 'value': value}))
    
    def pol_rem_attribute(self, group, attribute, value = None):
        if attribute in self.handled_attributes['services']:
            return self.pol_set_attribute(group, attribute, [])
    
    def set_attribute(self, change):
        service = change.parameters['group']
        attribute = change.parameters['attribute']
        value = change.parameters['value']
        configfile = self.pt.conf.get(['module-pam', 'pam-dir']) + '/' + service
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
                lines.append('account required pam_succeed_if.so user ingroup ' + group + "\n")
        elif attribute == 'groups_deny':
            for group in value:
                lines.append('account required pam_succeed_if.so user notingroup ' + group + "\n")
        elif attribute == 'users_allow':
            if len(value) == 1:
                lines.append('account required pam_succeed_if.so user = ' + value[0] + "\n")
            elif len(value) > 1:
                lines.append('account required pam_succeed_if.so user in ' + ':'.join(value) + "\n")
        elif attribute == 'users_deny':
            if len(value) == 1:
                lines.append('account required pam_succeed_if.so user != ' + value[0] + "\n")
            elif len(value) > 1:
                lines.append('account required pam_succeed_if.so user notin ' + ':'.join(value) + "\n")
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
                lines.append('password required pam_cracklib.so ' + ' '.join(args) + '\n')
        
        try:
            self.append_lines_to_file(configfile, before, after, attribute, lines)
        except IOError:
            return syspolicy.change.STATE_FAILED

        
        return syspolicy.change.STATE_COMPLETED
