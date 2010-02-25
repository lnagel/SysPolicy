#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy
import yaml

DEFAULT = "_default_"

class Config:
    def __init__(self,  source = None,  load = True):
        self.data = {}
        self.source = source
        if load and source:
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
    
    def compare_to(self,  other_config):
        if isinstance(other_config,  Config):
            return compare_trees(self.data,  other_config.data)


def compare_trees(a,  b):
    r = {}
    ak = set(a.keys())
    bk = set(b.keys())
    
    for key in ak.difference(bk):
        r[key] = copy.deepcopy(a[key])
    for key in bk.difference(ak):
        r[key] = None
    for key in ak.intersection(bk):
        if type(a[key]) is dict and type(b[key]) is dict:
            diff = compare_trees(a[key],  b[key])
            if diff:
                r[key] = diff
        if type(a[key]) is list and type(b[key]) is list:
            if set(a[key]).symmetric_difference(set(b[key])):
                r[key] = copy.deepcopy(a[key])
        elif type(a[key]) is not type(b[key]) or a[key] is not b[key]:
            r[key] = copy.deepcopy(a[key])
    return r
