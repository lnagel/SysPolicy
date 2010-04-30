#!/usr/bin/python
# -*- coding: utf-8 -*-

from syspolicy.policytool import PolicyTool
from syspolicy.modules.shadow import Shadow
from syspolicy.modules.pam import PAM
from syspolicy.modules.state import State
import yaml

pt = PolicyTool('config/main.conf')

pt.add_module(Shadow())
pt.add_module(PAM())
pt.add_module(State())

print yaml.dump(pt.get_policy_diff())

pt.get_policy_updates()

print yaml.dump(pt.state)

print "------- ChangeSets -------"
with pt.cs_mlock:
    for cs in pt.changesets:
        pt.accept_changeset(cs)
        print yaml.dump(cs)
        print "------"

pt.enqueue_changesets()

pt.worker.queue.join()
pt.save_state()

