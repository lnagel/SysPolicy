#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy

from config import Config, DEFAULT

class Policy(Config):
    
    def get(self, path = []):
        val = None
        if type(path) is list:
            val = self.get_branch(path)
            
            if len(path) >= 1:
                defpath = [DEFAULT] + path[1:]
                defval = self.get_branch(defpath)
                
                if val is None:
                    val = copy.deepcopy(defval)
                elif type(val) is dict and type(defval) is dict:
                    m = copy.deepcopy(defval)
                    merge_into(m, val)
                    val = m
        return val
        
def merge_into(base, overlay):
    #print "merge_into(", base, ",", overlay, ")"
    for key, item in overlay.items():
        if type(item) is dict and key in base and type(base[key]) is dict:
            merge_into(base[key], item)
        else:
            base[key] = item