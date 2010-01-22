#!/usr/bin/python
# -*- coding: utf-8 -*-

import yaml

DEFAULT = "_default_"

class Config:
    def __init__(self):
        self.data = {}
        
    def load(self, configfile):
        cf = file(configfile, 'r')
        self.data = yaml.load(cf)
        cf.close()
        
    def save(self, configfile):
        cf = file(configfile, 'w')
        yaml.dump(self.data, cf, default_flow_style=False)
        cf.close()
    
    def print_all(self):
        print yaml.dump(self.data, default_flow_style=False)
    
    def sections(self):
        return self.data.keys()
        
    def attributes(self, section = DEFAULT):
        if section in self.data and type(self.data[section]) is dict:
            return self.data[section].keys()
        else:
            return {}
        
    def get_branch(self, path = []):
        if type(path) is list:
            pos = self.data
            for node in path:
                if node in pos:
                    pos = pos[node]
                else:
                    return None
            return pos
        return None

    get = get_branch
