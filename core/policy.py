#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser
import yaml

DEFAULT_SECTION = "_default_"

class Policy:
    def __init__(self):
        self.parser = ConfigParser.SafeConfigParser()

    def load(self, configfiles):
        self.parser.read(configfiles)
        
        if DEFAULT_SECTION not in self.parser.sections():
            raise SyntaxError("Default section '" + DEFAULT_SECTION + "' not found in " + str(configfiles))

    def print_all(self):
        for section in self.sections():
            print "Section:", section
            for option in self.options():
                print " ", option, "=", self.get_option(section, option)
                
    def sections(self):
        if DEFAULT_SECTION in self.parser.sections():
            sections = self.parser.sections()
            sections.remove(DEFAULT_SECTION)
            return sections
        else:
            return self.parser.sections()
    
    def options(self, section = DEFAULT_SECTION):
        return self.parser.options(section)
    
    def get_option_raw(self, section, option):
        if self.parser.has_option(section, option):
            return self.parser.get(section, option)
        elif self.parser.has_option(DEFAULT_SECTION, option):
            context = {}
            for o in self.parser.options(section):
                context[o] = self.parser.get(section, o)
            return self.parser.get(DEFAULT_SECTION, option, 0, context)
        else:
            return None
    
    def get_option(self, section, option):
        value = self.get_option_raw(section, option)
        if value is not None:
            return yaml.load(value)
        else:
            return None