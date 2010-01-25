#!/usr/bin/python
# -*- coding: utf-8 -*-

from core import PolicyTool
from modules.shadow import Shadow
import yaml

pt = PolicyTool('config/main.conf')

pt.add_module(Shadow())
