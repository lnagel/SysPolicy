#!/usr/bin/python
# -*- coding: utf-8 -*-

from config import Config
from policy import Policy
from modules import Module

class PolicyTool:
    def __init__(self,  configfile):
        self.conf = Config(configfile)
        self.policy = {}
        self.state = {}
        self.handler = {}
        for type,  file in self.conf.get(['policy']).items():
            self.policy[type] = Policy(self.conf.get(['general', 'policy-path'])+'/'+file)
            try:
                self.state[type] = Policy(self.conf.get(['general', 'state-path'])+'/'+file)
            except IOError:
                self.state[type] = Policy(self.conf.get(['general', 'state-path'])+'/'+file,  False)
                self.state[type].save()
        self.module = {}
    
    def add_module(self,  module):
        if isinstance(module, Module):
            print module,  "is a module!"
            self.module[module.name] = module
            for policy_type,  attributes in module.handled_attributes.items():
                for attribute in attributes:
                    self.register_handler(policy_type,  attribute,  module)
    
    def register_handler(self,  policy_type,  attribute,  module):
        if policy_type not in self.handler:
            self.handler[policy_type] = {}
        if attribute not in self.handler[policy_type]:
            self.handler[policy_type][attribute] = module
            print "Registered handler: policy",  policy_type,  "attribute",  attribute,  "to",  module
        else:
            raise Exception("Handler has already been set for policy '" + policy_type + "' attribute '" + attribute + "'")


