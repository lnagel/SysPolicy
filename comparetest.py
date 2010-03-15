#!/usr/bin/python

from syspolicy.core.config import compare_trees
import yaml

a = {'aaa': 'hehehe',  'bbb': 'asdf',  'tree': {'asd': 1, 'kekekk': 42},  'list': ['a'], 'empty': None}
b = {'bbb': 'asd' ,  'tree': {'asd': 1}, 'list': ['a']}

r = compare_trees(a, b)
print yaml.dump(r, default_flow_style=False)
