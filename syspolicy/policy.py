# SysPolicy
# 
# Copyright (c) 2010 Lenno Nagel
# Author: Lenno Nagel <lenno-at-nagel.ee>
# URL: <http://trac.syspolicy.org>
# Released under the GNU General Public License version 3

"""
Policy class for handling policies
"""

import copy
from syspolicy.config import Config, DEFAULT

class Policy(Config):
    """
    This class extends the Config class to provide the policy functionality and
    meaning over a regular constant configuration object. This means that
    all the subsections are always expanded with the values from the default
    section recursively upon loading the policy.
    
    Secondly, the get() function has been overridden so that the default value
    is returned if the specified subsection or attribute doesn't exist. The 
    purpose of this behaviour is to always provide new groups with the default
    policy.
    """
    
    def __init__(self, name, source=None, load=True, merge_default=False):
        Config.__init__(self, name, source, load=False)
        if load and source:
            self.load(source, merge_default)
    
    def load(self, configfile=None, merge_default=False):
        """
        This function loads the policy from `configfile` and if
        `merge_default` is set to True, merges the default values
        into all the subsections as well.
        
        @param merge_default: Whether or not to merge the default values
        """
        Config.load(self, configfile)
        
        # If merge_default is True and we have a default section,
        # merge it's contents into other sections as well
        if merge_default and DEFAULT in self.data.keys():
            for section in set(self.data.keys()) - set([DEFAULT]):
                if type(self.data[section]) is dict:
                    self.data[section] = merge_into(
                                       copy.deepcopy(self.data[DEFAULT]),
                                       self.data[section])
    
    def get(self, path=[]):
        """
        This returns the policy data branch at `path` or if it doesn't exist,
        it returns the default value. If the value is a dictionary, it also
        merges in the default values for that attribute.
        """
        val = self.get_branch(path)
        
        if type(path) is list and path:
            defpath = [DEFAULT] + path[1:]
            defval = self.get_branch(defpath)
            
            if val is None and defval is not None:
                val = defval
            elif type(val) is dict and type(defval) is dict:
                val = merge_into(copy.deepcopy(defval), val)
        
        return val


def merge_into(base, overlay):
    """
    This function overlays the base dictionary with another one.
    
    @param base: The base dictionary
    @param overlay: The dictionary containing the new values
    @return: The merged result
    """
    for key, item in overlay.items():
        if type(item) is dict and key in base and type(base[key]) is dict:
            merge_into(base[key], item)
        else:
            base[key] = item
        
    return base
