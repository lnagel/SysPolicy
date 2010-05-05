#!/usr/bin/python
# -*- coding: utf-8 -*-

from optparse import OptionParser, OptionGroup

class OptParser(OptionParser):
    def __init__(self):
        OptionParser.__init__(self)
        
        # = Command line arguments =
        #* -h, --help
        #* -c, --config=FILE
        #* -u, --update
        #* -s, --scan
        #* --au, --add-user=USER
        #* --mu, --mod-user=USER
        #** -p, --password
        #** -n, --name=REALNAME
        #** -g, --group=GROUP
        #** --homedir/--no-homedir
        #* --du, --del-user=USER
        #* --ag, --add-group=GROUP
        #* --dg, --del-group=GROUP
        
        self.set_defaults(config='config/main.conf')
        self.set_defaults(mode_update=False)
        self.set_defaults(mode_scan=False)

        self.add_option("-c", "--config",
                dest="config", metavar="FILE", 
                help="load configuration from FILE")
      
        mode = OptionGroup(self, "Run modes")
        mode.add_option("-u", "--update",
                action="store_true", dest="mode_update",
                help="check for policy updates")
        mode.add_option("-s", "--scan",
                action="store_true", dest="mode_scan",
                help="perform a full system scan to verify the policy")
        self.add_option_group(mode)
        
        user = OptionGroup(self, "User management")
        user.add_option("--au", "--add-user",
                dest="add_user", metavar="USER", 
                help="Add a new user account")
        user.add_option("--mu", "--mod-user",
                dest="mod_user", metavar="USER", 
                help="Modify a user account")
        self.add_option_group(user)

