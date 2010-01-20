#!/usr/bin/python
# -*- coding: utf-8 -*-

from core.config import Config
from core.policy import Policy

config = Config()

config.load('config/main.conf')

gp = Policy()
gp.load(['config/groups.conf'])
gp.print_all()