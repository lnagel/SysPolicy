#!/usr/bin/python
# -*- coding: utf-8 -*-

from syspolicy.policytool import PolicyTool
from syspolicy.cli.prompt import confirm
import yaml
from syspolicy.cli.arguments import OptParser

def main():
    parser = OptParser()
    (options, args) = parser.parse_args()

    if options.mode_update:
        print "update mode!"
        
        pt = PolicyTool(options.config)
        pt.get_policy_updates()
        
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
    else:
        parser.print_help()

