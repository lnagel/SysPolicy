#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy
from syspolicy.config import Config, DEFAULT

class Policy(Config):
    
    def __init__(self, name, source=None, load=True, merge_default=False):
        Config.__init__(self, name, source, load=False)
        if load and source:
            self.load(source, merge_default)
    
    def load(self, configfile=None, merge_default=False):
        Config.load(self, configfile)
        
        # If merge_default is True and we have a default section,
        # merge it's contents into other sections as well
        if merge_default and DEFAULT in self.data.keys():
            for section in set(self.data.keys()) - set([DEFAULT]):
                if type(self.data[section]) is dict:
                    self.data[section] = merge_into(
                                       copy.deepcopy(self.data[DEFAULT]),
                                       self.data[section])
    
    def get(self, path = []):
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
    #print "merge_into(", base, ",", overlay, ")"
    for key, item in overlay.items():
        if type(item) is dict and key in base and type(base[key]) is dict:
            merge_into(base[key], item)
        else:
            base[key] = item
        
    return base
