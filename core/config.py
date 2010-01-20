#!/usr/bin/python
# -*- coding: utf-8 -*-

import yaml

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
        for section in self.data:
            print "Section:", section
            if self.data[section]:
                for option in self.data[section]:
                    print " ", option, "=", self.data[section][option]


