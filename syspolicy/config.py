#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy
import yaml

DEFAULT = "_default_"

CONFIG_ADDED = 1
CONFIG_CHANGED = 2
CONFIG_REMOVED = 3

class Config:
    def __init__(self, name, source=None, load=True):
        self.name = name
        self.data = {}
        self.source = source
        if load and source:
            self.load()
    
    def load(self, configfile=None):
        if configfile is None and self.source is not None:
            configfile = self.source
        if configfile is not None:
            cf = file(configfile, 'r')
            self.data = yaml.load(cf)
            cf.close()
            if type(self.data) is not dict:
                self.data = {}
            return True
        return False
    
    def save(self, configfile=None):
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
    
    def attributes(self, section=DEFAULT):
        if section in self.data and type(self.data[section]) is dict:
            return self.data[section].keys()
        else:
            return {}
    
    def get_branch(self, path=[]):
        return walk(self.data, path)

    get = get_branch
    
    def set(self, path, value):
        tpath = list(path)
        if type(path) is list:
            element = tpath.pop()
            branch = self.data
            
            for node in tpath:
                if node not in branch or type(branch[node]) is not dict:
                    branch[node] = {}
                branch = branch[node]
                    
            if value is not None:
                branch[element] = value
            elif element in branch:
                del branch[element]
            
            return True
        return False
    
    def compare_to(self, other_config):
        if isinstance(other_config, Config):
            return compare_trees(self.data, other_config.data)


def walk(tree, path=[]):
    if type(path) is list:
        branch = tree
        for node in path:
            if type(branch) is dict and node in branch:
                branch = branch[node]
            else:
                return None
        return branch
    return None

def compare_trees(a, b):
    r = {}
    ak = set(a.keys())
    bk = set(b.keys())
    
    for key in ak.difference(bk):
        r[key] = copy.deepcopy(a[key])
    for key in bk.difference(ak):
        if type(b[key]) is dict:
            r[key] = compare_trees({}, b[key])
        else:
            r[key] = None
    for key in ak.intersection(bk):
        if type(a[key]) is dict and type(b[key]) is dict:
            diff = compare_trees(a[key], b[key])
            if diff:
                r[key] = diff
        elif type(a[key]) is list and type(b[key]) is list:
            if set(a[key]).symmetric_difference(set(b[key])):
                r[key] = copy.deepcopy(a[key])
        elif type(a[key]) is not type(b[key]) or a[key] != b[key]:
            r[key] = copy.deepcopy(a[key])
    return r

def diff_type(a, b, path):
    a_branch = walk(a, path)
    b_branch = walk(b, path)
    if a_branch is None:
        return CONFIG_REMOVED
    elif b_branch is None:
        return CONFIG_ADDED
    return CONFIG_CHANGED
