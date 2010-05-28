# SysPolicy
# 
# Copyright (c) 2010 Lenno Nagel
# Author: Lenno Nagel <lenno-at-nagel.ee>
# URL: <http://trac.syspolicy.org>
# Released under the GNU General Public License version 3

"""
Common module functions and base class Module
"""

import re
import os
import os.path
import tempfile
import subprocess
import syspolicy.config
import syspolicy.change
from syspolicy.change import Change, ChangeSet
from syspolicy.policy import merge_into

class Module:
    """
    This is the base Module class that all other modules must extend.
    
    This provides the basic functionality that is expected from a module, 
    which includes the name of the module, handled attributes and diff
    operation handler functions, change operations and event hooks.
    """
    
    name = None #: the name of the module
    pt = None #: the PolicyTool instance that has loaded this module
    handled_attributes = None #: the attributes that this module handles
    diff_operations = None #: handlers for the various diff operations
    change_operations = None #: handlers for the various change operations
    event_hooks = None #: various event hooks that this module registers
    
    def __init__(self):
        self.name = "generic"
        self.handled_attributes = {}
        self.diff_operations = {
                            syspolicy.config.CONFIG_ADDED: self.cs_new_attribute,
                            syspolicy.config.CONFIG_CHANGED: self.cs_set_attribute,
                            syspolicy.config.CONFIG_REMOVED: self.cs_rem_attribute
                        }
        self.change_operations = {}
        self.change_operations['edit_configfile'] = self.edit_configfile
        self.event_hooks = {}

    def cs_check_diff(self, policy, operation, path, value, diff):
        """
        This function checks a difference in the policy and it's state at the
        location identified by `path` and `operation`. The function will
        attempt to find a handler for this change among the registered
        diff handlers in the PolicyTool.
        
        In case the handler is found, it is called and a ChangeSet is expected
        as the return value. If the ChangeSet is returned, an additional
        Change operation is appended to the list of changes for updating
        the internal state of that policy.
        
        Since that Change is appended to the
        end of the list, it is also executed last and only in the case the
        previous changes have succeeded.
        
        @param policy: Policy in which the difference was detected
        @param operation: type of the difference
        @param path: Location of the difference in the tree
        @param value: The new value that was set (None when it was removed)
        @param diff: The difference from the old value
        @return: This function always returns a ChangeSet
        """
        if self.pt.debug:
            print "cs_check_diff in:", policy, "operation:", operation, "for:", path, ",", diff
        cs = None
        
        # construct the state update Change
        state_update = Change("state", "set_state", 
                             {"policy": policy, "path": path,
                                "value": value, "diff_type": operation})
     
        if len(path) >= 2:
            group = path[0]
            attribute = path[1]
            
            # call the diff handler function
            if group == syspolicy.config.DEFAULT:
                cs = self.cs_set_default(attribute, value, diff)
            elif operation in self.diff_operations:
                cs = self.diff_operations[operation](group, attribute, value, diff)
        
        if cs is not None:
            # if a ChangeSet was returned, append the state update
            cs.append(state_update)
        else:
            # create a new ChangeSet containing only the state update
            cs = ChangeSet(state_update)
        
        return cs

    def cs_set_default(self, attribute, value, diff):
        """
        Null handler for setting a new default value in the policy.
        
        @param attribute: The attribute in the policy that is being set
        @param value: The new value
        @param diff: The difference from the old value
        @return: None
        """
        return None
    
    def cs_new_attribute(self, group, attribute, value, diff):
        """
        Default handler for setting a new attribute in the policy, which calls
        the cs_set_attribute and returns it's return value. This is a safe
        default, since usually there is no difference whether an attribute
        was added or simply modified.
        
        @param group: The group for which the attribute is being set
        @param attribute: The attribute in the policy that is being set
        @param value: The new value
        @param diff: The difference from the old value
        @return: A ChangeSet or None
        """
        return self.cs_set_attribute(group, attribute, value, diff)
    
    def cs_set_attribute(self, group, attribute, value, diff):
        """
        Null handler for modifying a value in the policy.
        
        @param group: The group for which the attribute is being set
        @param attribute: The attribute in the policy that is being set
        @param value: The new value
        @param diff: The difference from the old value
        @return: A ChangeSet or None
        """
        return None
    
    def cs_rem_attribute(self, group, attribute, value, diff):
        """
        Null handler for removing an attribute from the policy.
        
        @param group: The group for which the attribute is being set
        @param attribute: The attribute in the policy that is being set
        @param value: The new value
        @param diff: The difference from the old value
        @return: A ChangeSet or None
        """
        return None
    
    def perform_change(self, change):
        """
        This function accepts a Change object to be implemented and finds
        the respective function in the change_operations dict and calls it.
        
        In case the handler function is not found, STATE_NOT_HANDLED is
        returned.
        
        @param change: The Change that is to be implemented
        @return: Returns a state indicatation code or STATE_NOT_HANDLED
        """
        if change.operation in self.change_operations:
            return self.change_operations[change.operation](change)
        else:
            return syspolicy.change.STATE_NOT_HANDLED
    
    def edit_configfile(self, change):
        """
        This function implements the edit_configfile Change operation.
        
        It extracts the attributes from the Change element and calls
        the append_lines_to_file function.
        
        @param change: Change element to be implemented
        @return: STATE_COMPLETED on success, STATE_FAILED otherwise
        """
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
        """
        This function inserts lines to an existing configuration file.
        
        The new lines are surrounded with identifier tags which are
        detected in successive runs and so any previous countent
        with the same identifier tags is replaced.
        
        @param configfile: Path to the configuration file
        @param before: Regular expression to find before which line to add the new lines
        @param after: Regular expression to find after which line to add the new lines
        @param id: A simple identifier text to uniquely identify this section
        @param lines: List of strings to be inserted to the file
        @return: Returns True on success
        """
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
        """
        This function executes a system command.
        
        If the debug mode has been enabled, then the command is echoed
        back to the shell instead of executing it.
        
        @param cmd: The command to be executed with all the arguments as a list
        @return: STATE_COMPLETED when the return value is 0, otherwise STATE_FAILED
        """
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
