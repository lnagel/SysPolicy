#!/usr/bin/python
# -*- coding: utf-8 -*-

import yaml

from config import Config, DEFAULT

class Policy(Config):
    
    def get(self, section, attribute):
        if section in self.data and type(self.data[section]) is dict:
            if attribute in self.data[section]:
                return self.data[section][attribute]
        elif DEFAULT in self.data and type(self.data[DEFAULT]) is dict:
            if attribute in self.data[DEFAULT]:
                return self.data[DEFAULT][attribute]
                
        return None