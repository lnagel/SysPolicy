
import syspolicy.config
import syspolicy.change
from syspolicy.change import Change, ChangeSet
import re

class Module:
    def __init__(self):
        self.name = "generic"
        self.handled_attributes = {}
        self.pt = None
        self.diff_operations = {
                            syspolicy.config.CONFIG_ADDED: self.pol_new_attribute,
                            syspolicy.config.CONFIG_CHANGED: self.pol_set_attribute,
                            syspolicy.config.CONFIG_REMOVED: self.pol_rem_attribute
                        }
        self.change_operations = {}

    def pol_check_diff(self, policy, operation, path, value):
        print "pol_check_diff in:", policy, "operation:", operation, "for:",  path, ",", value
        cs = None
        state_update = Change("state", "set_state", 
                             {"policy": policy, "path": path,
                             "value": value, "diff_type": operation})
     
        if len(path) >= 2:
            group = path[0]
            attribute = path[1]
            
            if group == syspolicy.config.DEFAULT:
                print "assign default setting:", attribute, "=", value
                cs = self.pol_set_default(attribute, value)
            elif operation in self.diff_operations:
                cs = self.diff_operations[operation](group, attribute, value)
        
        if cs is not None:
            cs.append(state_update)
        else:
            cs = ChangeSet(state_update)
        
        return cs

    def pol_set_default(self, attribute, value):
        return None
    
    def  pol_new_attribute(self, group, attribute, value):
        return self.pol_set_attribute(group, attribute, value)
    
    def pol_set_attribute(self, group, attribute, value):
        return None
    
    def pol_rem_attribute(self, group, attribute, value = None):
        return None
    
    def perform_change(self, change):
        if change.operation in self.change_operations:
            return self.change_operations[change.operation](change)
        else:
            return syspolicy.change.STATE_NOT_HANDLED
    
    def append_lines_to_file(self, configfile, before, after, id, lines):
        orig_file = open(configfile, "r")
        orig_src = orig_file.readlines()
        src = []
        dst = []
        orig_file.close()
        inserted = False
        
        tag = "SysPolicy module " + self.name + " -- " + id
        start_tag = "### BEGIN " + tag + " ###\n"
        end_tag = "### END " + tag + " ### \n"
        lines.insert(0, start_tag)
        lines.append(end_tag)
        
        filter = False
        for line in orig_src:
            if re.search('^' + start_tag, line):
                filter = True
            if not filter:
                src.append(line)
            if filter and re.search('^' + end_tag, line):
                filter = False                
        
        print
        print orig_src
        print id
        print lines
        
        if before is not None:
            for line in src:
                if not inserted and re.search(before, line.rstrip("\r\n")):
                    dst.extend(lines)
                    inserted = True
                dst.append(line)
        elif after is not None:
            for line in src:
                dst.append(line)
                if not inserted and re.search(after, line.rstrip("\r\n")):
                    dst.extend(lines)
                    inserted = True
        else:
            dst.extend(src)
        
        if not inserted:
            dst.extend(lines)
        
        print 40 * "-"
        for d in dst:
            print d, 

        #new_file = open(new_filename, "w")
        #new_file.writelines(lines)
        

    
