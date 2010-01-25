#!/usr/bin/python
# -*- coding: utf-8 -*-

import yaml

quota = {'/': '100M', '/srv': 0}

data = {'this variable': 'that'}
#data['userquota'] = quota

groups = {}
groups['users'] = data

print yaml.dump(yaml.load("""
_default_:
    basedir: /home
    uid_min: 1000
    uid_max: 2000
    gid_min: uid_min
    gid_max: uid_min

    usergroups: false
    grouphomes: false

    userquota: {}

users:
    usergroups: true

www-users:
    basedir: /srv
    grouphomes: true
    usergroups: true
    uid_min: 10000
    uid_max: 12000

    userquota:
        /srv: 100M
        /var: 0
"""))


services = {}
services['_default_'] = {}
services['sshd'] = {}
services['sshd']['allow_groups'] = ['users', 'sshusers']
services['sshd']['deny_groups'] = ['www-users']
services['sshd']['allow_users'] = ['lenno', 'backuppc']
services['sshd']['deny_users'] = ['root']

print yaml.dump(services)