#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import with_statement

from syspolicy.policytool import PolicyTool
from syspolicy.cli.prompt import confirm
import yaml
from syspolicy.cli.arguments import OptParser

def main():
    parser = OptParser()
    (opts, args) = parser.parse_args()
    
    o = [opts.mode_update, opts.mode_scan, opts.add_user, 
              opts.mod_user, opts.del_user, opts.add_group, opts.del_group]
    
    # How many values that we have that aren't None or False?
    if len(o) - o.count(None) - o.count(False) != 1:
        parser.error("You have to specify exactly 1 run mode option")
    
    pt = PolicyTool(opts.config)

    if opts.mode_update:
        print "update mode!"
        pt.get_policy_updates()
    elif opts.mode_scan:
        # TODO: Implement the scan mode
        parser.error("Sorry, the scan mode isn't supported yet")
    
    print "------- ChangeSets -------"
    with pt.cs_mlock:
        for cs in pt.changesets:
            print yaml.dump(cs)
            pt.accept_changeset(cs, confirm("Approve this ChangeSet?"))
    
    if len(pt.changesets) > 0 and confirm("Enqueue %d ChangeSets?" % len(pt.changesets)):
        pt.enqueue_changesets()
    else:
        print "Nothing to do.."
    
    pt.worker.queue.join()
    pt.save_state()

