#!/usr/bin/python
# -*- coding: utf-8 -*-

from core.config import Config
from core.policy import Policy

print '-' * 40

config = Config()
config.load('config/main.conf')
config.print_all()

print '-' * 10, "sections & attributes", '-' * 10

for section in config.sections():
    print section, ":", config.attributes(section)

print '-' * 40

gp = Policy()
gp.load('config/groups.conf')
gp.print_all()

print '-' * 40