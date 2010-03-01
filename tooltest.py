#!/usr/bin/python
# -*- coding: utf-8 -*-

from core import PolicyTool
from modules.shadow import Shadow
import yaml

pt = PolicyTool('config/main.conf')

pt.add_module(Shadow())

print yaml.dump(pt.get_policy_diff())

pt.get_policy_updates()

pt.set_state('groups', ['www-users', 'userquota', '/srv'], '100M')

print yaml.dump(pt.state)
pt.save_state()

print "------- ChangeSets -------"
for cs in pt.changesets:
    print yaml.dump(cs)
    print "------"

