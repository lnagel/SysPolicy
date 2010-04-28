
import syspolicy.change
from syspolicy.change import Change, ChangeSet
from syspolicy.modules.module import Module
import os

class PAM(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "pam"
        self.handled_attributes['services'] = ['groups_allow',  'groups_deny',  'users_allow',  'users_deny']
        self.change_operations['set_default'] = self.set_default
        self.change_operations['set_attribute'] = self.set_attribute
    
    def pol_set_default(self, attribute,  value):
        print "Setting new default in the PAM module", attribute, "=", value
        return ChangeSet(Change("shadow", "set_default", {attribute: value}))
    
    def pol_set_attribute(self, group, attribute, value):
        print "Setting attribute value in the PAM module", attribute, "=", value
        return ChangeSet(Change(self.name, "set_attribute", {'group': group, 'attribute': attribute, 'value': value}))
    
    def pol_rem_attribute(self, group, attribute, value = None):
        if attribute in ['groups_allow',  'groups_deny',  'users_allow',  'users_deny']:
            return self.pol_set_attribute(group, attribute, [])
    
    def set_default(self, change):
        return syspolicy.change.STATE_COMPLETED
    
    def set_attribute(self, change):
        service = change.parameters['group']
        attribute = change.parameters['attribute']
        value = change.parameters['value']
        configfile = self.pt.conf.get(['module-pam', 'pam-dir']) + '/' + service
        lines = []
        
        if not os.access(configfile, os.F_OK):
            raise Exception("PAM service config file '" + configfile + "' does not exist")
        
        # TODO: Make this function work with more than one group per attribute
        if len(value) > 1:
            raise Exception("Cannot handle more than 1 group the attribute " + attribute + " yet")
        
        if attribute == 'groups_allow':
            for group in value:
                lines.append('auth requisite pam_succeed_if.so quiet_success user ingroup ' + group + "\n")
        elif attribute == 'groups_deny':
            for group in value:
                lines.append('auth requisite pam_succeed_if.so quiet_success user notingroup ' + group + "\n")
        
        try:
            self.append_lines_to_file(configfile, '^account', None, attribute, lines)
        except IOError:
            return syspolicy.change.STATE_FAILED

        
        return syspolicy.change.STATE_COMPLETED
