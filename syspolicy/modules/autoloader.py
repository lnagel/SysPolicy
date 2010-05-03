from syspolicy.modules.shadow import Shadow
from syspolicy.modules.pam import PAM
from syspolicy.modules.state import State

def autoload_modules(pt):
    pt.add_module(Shadow())
    pt.add_module(PAM())
    pt.add_module(State())
