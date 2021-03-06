# SysPolicy
# 
# Copyright (c) 2010 Lenno Nagel
# Author: Lenno Nagel <lenno-at-nagel.ee>
# URL: <http://trac.syspolicy.org>
# Released under the GNU General Public License version 3

"""Module auto-loader"""

from syspolicy.modules.shadow import Shadow
from syspolicy.modules.pam import PAM
from syspolicy.modules.quota import Quota
from syspolicy.modules.state import State

def autoload_modules(pt):
    """
    Auto-load the currently available modules to the PolicyTool.
    
    @param pt: The PolicyTool in which the modules are to be loaded.
    """
    pt.add_module(Shadow())
    pt.add_module(PAM())
    pt.add_module(Quota())
    pt.add_module(State())
