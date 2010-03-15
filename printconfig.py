#!/usr/bin/python
# -*- coding: utf-8 -*-

from syspolicy.core.config import Config
from syspolicy.core.policy import Policy

print '-' * 40

config = Config('config/main.conf')
config.print_all()

print '-' * 9, "sections & attributes", '-' * 8

for section in config.sections():
    print section, ":", config.attributes(section)

print '-' * 40

print config.get(['passwords', 'min_length'])

print '-' * 40

gp = Policy('config/groups.conf')
gp.print_all()

print '-' * 40

print "users:", gp.get(['users'])
print "users->userquota:", gp.get(['users', 'userquota'])
print "users->userquota->/var:", gp.get(['users', 'userquota', '/var'])

print '-' * 40

print "www-users:", gp.get(['www-users'])
print "www-users->userquota:", gp.get(['www-users', 'userquota'])
print "www-users->userquota->/var:", gp.get(['www-users', 'userquota', '/var'])

print '-' * 40
