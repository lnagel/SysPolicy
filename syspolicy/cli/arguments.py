#!/usr/bin/python
# -*- coding: utf-8 -*-

from optparse import OptionParser

class OptParser(OptionParser):
    def __init__(self):
        OptionParser.__init__(self)

        self.add_option("-c", "--config", 
              action="store", dest="config", default="config/main.conf", 
              help="load configuration from FILE", metavar="FILE")
        self.add_option("-u", "--update",
              action="store_true", dest="mode_update", default=False,
              help="check for policy updates")
        self.add_option("-s", "--scan",
              action="store_true", dest="mode_scan", default=False,
              help="perform a full system scan to verify the policy")
