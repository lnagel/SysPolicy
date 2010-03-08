#!/usr/bin/python
# -*- coding: utf-8 -*-

from core import PolicyTool
import core.change
from modules.shadow import Shadow
import yaml
import time

pt = PolicyTool('config/main.conf')

pt.add_module(Shadow())

print yaml.dump(pt.get_policy_diff())

pt.get_policy_updates()

pt.set_state('groups', ['www-users', 'userquota', '/srv'], '100M')

print yaml.dump(pt.state)
pt.save_state()

print "------- ChangeSets -------"
with pt.cs_mlock:
    for cs in pt.changesets:
        with pt.cs_locks[cs]:
            cs.set_state(core.change.STATE_ACCEPTED)
            print yaml.dump(cs)
        print "------"

pt.enqueue_changesets()

time.sleep(2)

