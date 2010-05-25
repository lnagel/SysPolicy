#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import syspolicy.change
from syspolicy.policytool import PolicyTool
from syspolicy.cli.prompt import confirm, setpwd
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
    
    pt = PolicyTool(opts.config, debug=opts.debug)
    shadow = pt.module['shadow']
    cs = None
    password = None

    if opts.mode_update:
        pt.get_policy_updates()
        pt.accept_state_changes()
    elif opts.mode_scan:
        pt.clear_state()
        pt.get_policy_updates()
        pt.accept_state_changes()
    elif opts.add_user is not None:
        if type(opts.group) != list or len(opts.group) < 1:
            parser.error("You have to specify at least 1 group")
        
        if opts.password:
            password = setpwd(shadow.get_password_policy())
        group = opts.group.pop(0)
        policy = parser.parse_policy(opts)
        
        cs = shadow.cs_add_user(username=opts.add_user,
                            group=group,
                            extragroups=opts.group, 
                            name=opts.name, 
                            homedir=opts.homedir, 
                            password=password, 
                            policy=policy)
        pt.add_changeset(cs)
    elif opts.mod_user is not None:
        policy = parser.parse_policy(opts)
        
        if opts.password:
            password = setpwd(shadow.get_password_policy())
        
        # check if editing groups is requested
        if opts.group is not None:
            if type(opts.group) != list or len(opts.group) < 1:
                parser.error("You have to specify at least 1 group")
            
            group = opts.group.pop(0)
            
            cs = shadow.cs_mod_user(username=opts.mod_user,
                                group=group,
                                extragroups=opts.group, 
                                name=opts.name,
                                password=password, 
                                homedir=opts.homedir, 
                                policy=policy)
        else:
            cs = shadow.cs_mod_user(username=opts.mod_user,
                                name=opts.name, 
                                password=password, 
                                homedir=opts.homedir, 
                                policy=policy)
        
        pt.add_changeset(cs)
    elif opts.del_user is not None:
        cs = shadow.cs_del_user(username=opts.del_user)
        pt.add_changeset(cs)
    elif opts.add_group is not None:
        cs = shadow.cs_add_group(group=opts.add_group)
        pt.add_changeset(cs)
    elif opts.del_group is not None:
        cs = shadow.cs_del_group(group=opts.del_group)
        pt.add_changeset(cs)
    
    print "------- ChangeSets -------"
    with pt.cs_mlock:
        for cs in pt.changesets:
            print yaml.dump(cs)
            if cs.state == syspolicy.change.STATE_PROPOSED:
                pt.accept_changeset(cs, confirm("Approve this ChangeSet?"))
            print "==> This ChangeSet is", syspolicy.change._state_strings[cs.state]
            print
    
    accepted = pt.changesets_with_state(syspolicy.change.STATE_ACCEPTED)
    print "------- %d accepted ChangeSets -------" % len(accepted)
    
    for cs in accepted:
        print "* ChangeSet %d:" % (accepted.index(cs) + 1), 
        descr = []
        for c in cs.changes:
            descr.append(c.subsystem + ":" + c.operation)
        print ', '.join(descr)
    
    if len(accepted) > 0 and confirm("Enqueue %d ChangeSets?" % len(accepted)):
        pt.enqueue_changesets(accepted)
    else:
        print "Nothing to do.."
    
    pt.worker.queue.join()
    pt.save_state()

