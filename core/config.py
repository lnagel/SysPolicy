#!/usr/bin/python
# -*- coding: utf-8 -*-

import yaml

DEFAULT = "_default_"

class Config:
    def __init__(self,  source = None):
        self.data = {}
        self.source = source
        self.load()
    
    def load(self, configfile = None):
        if configfile is None and self.source is not None:
            configfile = self.source
        if configfile is not None:
            cf = file(configfile, 'r')
            self.data = yaml.load(cf)
            cf.close()
            return True
        return False
        
    def save(self, configfile = None):
        if configfile is None and self.source is not None:
            configfile = self.source
        if configfile is not None:
            cf = file(configfile, 'w')
            yaml.dump(self.data, cf, default_flow_style=False)
            cf.close()
            return True
        return False
    
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
            branch = self.data
            for node in path:
                if node in branch:
                    branch = branch[node]
                else:
                    return None
            return branch
        return None

    get = get_branch
