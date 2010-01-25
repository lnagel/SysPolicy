#!/usr/bin/python
# -*- coding: utf-8 -*-

from config import Config
from policy import Policy
from modules import Module

class PolicyTool:
    def __init__(self,  configfile):
        self.conf = Config(configfile)
        self.pol = {}
        self.handlers = {}
        for type,  file in self.conf.get(['policy']).items():
            self.pol[type] = Policy(file)
        self.mods = {}
    
    def add_module(self,  module):
        if isinstance(module, Module):
            print module,  "is a module!"
            self.mods[module.name] = module
            for policy_type,  attributes in module.handled_attributes.items():
                for attribute in attributes:
                    self.register_handler(policy_type,  attribute,  module)
    
    def register_handler(self,  policy_type,  attribute,  module):
        if policy_type not in self.handlers:
            self.handlers[policy_type] = {}
        if attribute not in self.handlers[policy_type]:
            self.handlers[policy_type][attribute] = module
            print "Registered handler: policy",  policy_type,  "attribute",  attribute,  "to",  module
        else:
            raise Exception("Handler has already been set for policy '" + policy_type + "' attribute '" + attribute + "'")
