#!/usr/bin/python
# -*- coding: utf-8 -*-

from syspolicy.policytool import PolicyTool
import yaml

pt = PolicyTool('config/main.conf')

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

