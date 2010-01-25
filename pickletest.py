#!/usr/bin/python
# -*- coding: utf-8 -*-

import pickle
import yaml

quota = {'/': '100M'}

print str(quota)
print pickle.dumps(quota)
print yaml.dump(quota)
