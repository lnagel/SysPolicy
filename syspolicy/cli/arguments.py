#!/usr/bin/python
# -*- coding: utf-8 -*-

from optparse import OptionParser, OptionGroup

class OptParser(OptionParser):
    def __init__(self):
        OptionParser.__init__(self)
        
        self.set_defaults(config='config/main.conf')
        self.set_defaults(debug=False)
        self.set_defaults(mode_update=False)
        self.set_defaults(mode_scan=False)

        self.add_option("-c", "--config",
                dest="config", metavar="FILE", 
                help="load configuration from FILE")
        self.add_option("-D", "--debug",
                dest="debug", action="store_true", 
                help="enable debug code-paths")
        
        mode = OptionGroup(self, "Run mode")      
        mode.add_option("-u", "--update",
                action="store_true", dest="mode_update",
                help="check for policy updates")
        mode.add_option("--scan",
                action="store_true", dest="mode_scan",
                help="perform a full system scan to verify the policy")
        mode.add_option("--au", "--add-user",
                dest="add_user", metavar="USER", 
                help="Add a new user account")
        mode.add_option("--mu", "--mod-user",
                dest="mod_user", metavar="USER", 
                help="Modify a user account")
        mode.add_option("--du", "--del-user",
                dest="del_user", metavar="USER", 
                help="Remove a user account")
        mode.add_option("--ag", "--add-group",
                dest="add_group", metavar="GROUP", 
                help="Add a new group")
        mode.add_option("--dg", "--del-group",
                dest="del_group", metavar="GROUP", 
                help="Remove a group")
        self.add_option_group(mode)
        
        user = OptionGroup(self, "User account parameters")
        user.add_option("-b", "--base-dir",
                dest="basedir", metavar="DIR", 
                help="override the base directory path")
        user.add_option("-n", "--name",
                dest="name", metavar="NAME", 
                help="comment the account (eg. real name of the person)")
        user.add_option("-d", "--home-dir",
                dest="homedir", metavar="DIR", 
                help="override the home directory path")
        user.add_option("-e", "--expiredate",
                dest="expire", metavar="DAYS", 
                help="set account expiration date in days from now")
        user.add_option("-i", "--inactive",
                dest="inactive", metavar="DAYS", 
                help="set account inactive period after password expiry")
        user.add_option("-g", "--group",
                dest="group", action="append", metavar="GROUP", 
                help="set account as member of GROUP; when specified multiple "
                        "times, the group specified first is considered primary")
        user.add_option("-k", "--skel",
                dest="skeleton", metavar="DIR", 
                help="override the skeleton directory")
        user.add_option("-m", "--create-home",
                dest="create_homedir", action="store_true", 
                help="force the creation of a home directory [default]")
        user.add_option("-N", "--no-home",
                dest="create_homedir", action="store_false", 
                help="skip the creation of a home directory")
        user.add_option("-s", "--shell",
                dest="shell", metavar="SHELL", 
                help="override the login shell")
        user.add_option("-p", "--password",
                dest="password", action="store_true", 
                help="prompt for a new password")
        self.add_option_group(user)
    
    def parse_policy(self, opts):
        policy = {}
        if opts.basedir is not None:
            policy['basedir'] = opts.basedir
        if opts.expire is not None:
            policy['expire'] = int(opts.expire)
        if opts.inactive is not None:
            policy['inactive'] = int(opts.inactive)
        if opts.skeleton is not None:
            policy['skeleton'] = opts.skeleton
        if opts.create_homedir is not None:
            policy['create_homedir'] = opts.create_homedir
        if opts.shell is not None:
            policy['shell'] = opts.shell
        return policy
