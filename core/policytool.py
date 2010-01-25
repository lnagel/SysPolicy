#!/usr/bin/python
# -*- coding: utf-8 -*-

from config import Config 
from policy import Policy

class PolicyTool:
    def __init__(self,  configfile):
        self.conf = Config(configfile)
        self.pol = {}
        for type,  path in self.conf.get(['policy']).items():
            self.pol[type] = Policy(path)
