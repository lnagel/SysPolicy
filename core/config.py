#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser

class Config:
    def __init__(self):
        self.parser = ConfigParser.ConfigParser()
        
    def load(self, configfiles):
        self.parser.read(configfiles)
    
    def printall(self):
        for section in self.parser.sections():
            print "Section:", section
            for option in self.parser.options(section):
                print " ", option, "=", self.parser.get(section, option)


