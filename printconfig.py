#!/usr/bin/python
# -*- coding: utf-8 -*-

from core.config import Config
from core.policy import Policy

print '-' * 40

config = Config()
config.load('config/main.conf')
config.print_all()

print '-' * 9, "sections & attributes", '-' * 8

for section in config.sections():
    print section, ":", config.attributes(section)

print '-' * 40

print config.get(['passwords', 'min_length'])

print '-' * 40

gp = Policy()
gp.load('config/groups.conf')
gp.print_all()

print '-' * 40

print "users:", gp.get(['users'])
print "users->userquota:", gp.get(['users', 'userquota'])

print '-' * 40

print "www-users:", gp.get(['www-users'])
print "www-users->userquota:", gp.get(['www-users', 'userquota'])

print '-' * 40