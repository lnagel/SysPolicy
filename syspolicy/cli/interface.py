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
    pt.debug = opts.debug
    cs = None

    if opts.mode_update:
        print "update mode!"
        pt.get_policy_updates()
    elif opts.mode_scan:
        # TODO: Implement the scan mode
        parser.error("Sorry, the scan mode isn't supported yet")
    elif opts.add_user is not None:
        print "add user mode!"
        if type(opts.group) != list or len(opts.group) < 1:
            parser.error("You have to specify at least 1 group")
        
        group = opts.group.pop(0)
        policy = parser.parse_policy(opts)
        
        cs = pt.module['shadow'].cs_add_user(username=opts.add_user,
                            group=group,
                            extragroups=opts.group, 
                            name=opts.name, 
                            homedir=opts.homedir, 
                            policy=policy)
        pt.add_changeset(cs)
    elif opts.mod_user is not None:
        print "mod user mode!"
        policy = parser.parse_policy(opts)
        
        # check if editing groups is requested
        if opts.group is not None:
            if type(opts.group) != list or len(opts.group) < 1:
                parser.error("You have to specify at least 1 group")
            
            group = opts.group.pop(0)
            
            cs = pt.module['shadow'].cs_mod_user(username=opts.mod_user,
                                group=group,
                                extragroups=opts.group, 
                                name=opts.name, 
                                homedir=opts.homedir, 
                                policy=policy)
        else:
            cs = pt.module['shadow'].cs_mod_user(username=opts.mod_user,
                                name=opts.name, 
                                homedir=opts.homedir, 
                                policy=policy)
        
        pt.add_changeset(cs)
    elif opts.del_user is not None:
        cs = pt.module['shadow'].cs_del_user(username=opts.del_user)
        pt.add_changeset(cs)
    elif opts.add_group is not None:
        cs = pt.module['shadow'].cs_add_group(group=opts.add_group)
        pt.add_changeset(cs)
    elif opts.del_group is not None:
        cs = pt.module['shadow'].cs_del_group(group=opts.del_group)
        pt.add_changeset(cs)
    
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

