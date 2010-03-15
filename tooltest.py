#!/usr/bin/python
# -*- coding: utf-8 -*-

import syspolicy.core.change
from syspolicy.core.policytool import PolicyTool
from syspolicy.modules.shadow import Shadow
from syspolicy.modules.state import State
import yaml
import time

pt = PolicyTool('config/main.conf')

pt.add_module(Shadow())
pt.add_module(State())

print yaml.dump(pt.get_policy_diff())

pt.get_policy_updates()

print yaml.dump(pt.state)

print "------- ChangeSets -------"
with pt.cs_mlock:
    for cs in pt.changesets:
        with pt.cs_locks[cs]:
            cs.set_state(syspolicy.core.change.STATE_ACCEPTED)
            print yaml.dump(cs)
        print "------"

pt.enqueue_changesets()

time.sleep(2)
pt.save_state()

