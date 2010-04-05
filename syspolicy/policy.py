#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy
from syspolicy.config import Config, DEFAULT

class Policy(Config):
    
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
