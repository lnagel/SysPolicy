# SysPolicy
# 
# Copyright (c) 2010 Lenno Nagel
# Author: Lenno Nagel <lenno-at-nagel.ee>
# URL: <http://trac.syspolicy.org>
# Released under the GNU General Public License version 3

import syspolicy.config
import syspolicy.change
from syspolicy.change import Change, ChangeSet
from syspolicy.policy import merge_into
import re
import os
import os.path
import tempfile
import subprocess

class Module:
    def __init__(self):
        self.name = "generic"
        self.handled_attributes = {}
        self.pt = None
        self.diff_operations = {
                            syspolicy.config.CONFIG_ADDED: self.cs_new_attribute,
                            syspolicy.config.CONFIG_CHANGED: self.cs_set_attribute,
                            syspolicy.config.CONFIG_REMOVED: self.cs_rem_attribute
                        }
        self.change_operations = {}
        self.change_operations['edit_configfile'] = self.edit_configfile
        self.event_hooks = {}

    def cs_check_diff(self, policy, operation, path, value, diff):
        if self.pt.debug:
            print "cs_check_diff in:", policy, "operation:", operation, "for:", path, ",", diff
        cs = None
        state_update = Change("state", "set_state", 
                             {"policy": policy, "path": path,
                                "value": value, "diff_type": operation})
     
        if len(path) >= 2:
            group = path[0]
            attribute = path[1]
            
            if group == syspolicy.config.DEFAULT:
                cs = self.cs_set_default(attribute, value, diff)
            elif operation in self.diff_operations:
                cs = self.diff_operations[operation](group, attribute, value, diff)
        
        if cs is not None:
            cs.append(state_update)
        else:
            cs = ChangeSet(state_update)
        
        return cs

    def cs_set_default(self, attribute, value, diff):
        return None
    
    def cs_new_attribute(self, group, attribute, value, diff):
        return self.cs_set_attribute(group, attribute, value, diff)
    
    def cs_set_attribute(self, group, attribute, value, diff):
        return None
    
    def cs_rem_attribute(self, group, attribute, value, diff):
        return None
    
    def perform_change(self, change):
        if change.operation in self.change_operations:
            return self.change_operations[change.operation](change)
        else:
            return syspolicy.change.STATE_NOT_HANDLED
    
    def edit_configfile(self, change):
        p = change.parameters
        try:
            self.append_lines_to_file(p['configfile'],
                                      p['before'],
                                      p['after'],
                                      p['id'],
                                      p['lines'])
        except IOError:
            return syspolicy.change.STATE_FAILED
        
        return syspolicy.change.STATE_COMPLETED
    
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
        
        elines = []
        for line in lines:
            elines.append(line + '\n')
        
        if len(elines) > 0:
            elines.insert(0, start_tag)
            elines.append(end_tag)
        
        filter = False
        for line in orig_src:
            if re.search('^' + start_tag, line):
                filter = True
            if not filter:
                src.append(line)
            if filter and re.search('^' + end_tag, line):
                filter = False                
        
        seek_for_end = False
        if before is not None or after is not None:
            for line in src:
                if not seek_for_end and re.search('^### BEGIN', line.rstrip("\r\n")):
                    seek_for_end = True
                elif seek_for_end and re.search('^### END', line.rstrip("\r\n")):
                    seek_for_end = False
                
                if before is not None and not seek_for_end and not inserted and re.search(before, line.rstrip("\r\n")):
                    dst.extend(elines)
                    inserted = True
                
                dst.append(line)
                
                if after is not None and not seek_for_end and not inserted and re.search(after, line.rstrip("\r\n")):
                    dst.extend(elines)
                    inserted = True
        else:
            dst.extend(src)
        
        if not inserted:
            dst.extend(elines)
        
        if self.pt.debug:
            print
            print 40 * "-"
            for d in dst:
                print d, 
            print 40 * "-"

        basename = os.path.basename(configfile)
        basedir = os.path.dirname(configfile)
        
        temp_file = tempfile.NamedTemporaryFile(prefix='.'+basename+'.', suffix='.syspolicy', dir=basedir, delete=False)
        temp_file.writelines(dst)
        temp_file.close()
        
        if self.pt.debug:
            os.remove(temp_file.name)
        else:
            os.rename(temp_file.name, configfile)
        
        return True
    
    def execute(self, cmd=[]):
        if self.pt.debug:
            cmd = ['/bin/echo'] + cmd
        
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        p.wait()
        
        if self.pt.debug:
            print '>>>', stdout, 
        
        if p.returncode == 0:
            return syspolicy.change.STATE_COMPLETED
        elif stderr:
            raise Exception('Executing: ' + ' '.join(cmd) + '\n' + stderr)
        else:
            return syspolicy.change.STATE_FAILED
