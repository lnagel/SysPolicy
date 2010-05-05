#!/usr/bin/python
# -*- coding: utf-8 -*-

from optparse import OptionParser, OptionGroup

class OptParser(OptionParser):
    def __init__(self):
        OptionParser.__init__(self)
        
        self.set_defaults(config='config/main.conf')
        self.set_defaults(mode_update=False)
        self.set_defaults(mode_scan=False)

        self.add_option("-c", "--config",
                dest="config", metavar="FILE", 
                help="load configuration from FILE")
      
        self.add_option("-u", "--update",
                action="store_true", dest="mode_update",
                help="check for policy updates")
        self.add_option("--scan",
                action="store_true", dest="mode_scan",
                help="perform a full system scan to verify the policy")
        
        ug = OptionGroup(self, "User & group management")
        ug.add_option("--au", "--add-user",
                dest="add_user", metavar="USER", 
                help="Add a new user account")
        ug.add_option("--mu", "--mod-user",
                dest="mod_user", metavar="USER", 
                help="Modify a user account")
        ug.add_option("--du", "--del-user",
                dest="del_user", metavar="USER", 
                help="Remove a user account")
        ug.add_option("--ag", "--add-group",
                dest="add_group", metavar="GROUP", 
                help="Add a new group")
        ug.add_option("--dg", "--del-group",
                dest="del_group", metavar="GROUP", 
                help="Remove a group")
        self.add_option_group(ug)
        
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
        user.add_option("-N", "--no-homedir",
                dest="no_homedir", action="store_true", 
                help="do not create a home directory for the user account")
        user.add_option("-s", "--shell",
                dest="shell", metavar="SHELL", 
                help="override the login shell")
        user.add_option("-U", "--user-group",
                dest="usergroup", action="store_true", 
                help="create a user group")
        self.add_option_group(user)

