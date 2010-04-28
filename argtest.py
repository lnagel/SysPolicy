#!/usr/bin/python
# -*- coding: utf-8 -*-

from syspolicy.policytool import PolicyTool
from syspolicy.modules.shadow import Shadow
from syspolicy.modules.state import State
import yaml
from optparse import OptionParser

parser = OptionParser()

parser.add_option("-u", "--update",
                  action="store_true", dest="mode_update", default=False,
                  help="check for policy updates")
parser.add_option("-s", "--scan",
                  action="store_true", dest="mode_scan", default=False,
                  help="perform a full system scan to verify the policy")

(options, args) = parser.parse_args()

if options.mode_update:
    print "update mode!"
    
    pt = PolicyTool('config/main.conf')
    pt.add_module(Shadow())
    pt.add_module(State())
    pt.get_policy_updates()
    
    print "------- ChangeSets -------"
    with pt.cs_mlock:
        for cs in pt.changesets:
            print yaml.dump(cs)
    
    pt.save_state()
else:
    parser.print_help()

