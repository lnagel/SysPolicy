# SysPolicy
# 
# Copyright (c) 2010 Lenno Nagel
# Author: Lenno Nagel <lenno-at-nagel.ee>
# URL: <http://trac.syspolicy.org>
# Released under the GNU General Public License version 3

"""
Base configuration class Config and comparison functions
"""

import copy
import yaml

DEFAULT = "_default_" #: the config section containing the defaults

CONFIG_ADDED = 1
CONFIG_CHANGED = 2
CONFIG_REMOVED = 3

class Config:
    name = None #: the identifier name for this Config
    data = None #: the data dictionary tree
    source = None #: the source configuration file
    
    def __init__(self, name, source=None, load=True):
        """
        Initialize the Config class and load the configuration if `load` is True
        
        @param name: The identifier name for the Config
        @param source: Source file name where to load/save the configuration
        @param load: Whether to load the configuration at start (default: True)
        """
        self.name = name
        self.data = {}
        self.source = source
        if load and source:
            self.load()
    
    def load(self, configfile=None):
        """
        Function that loads the configuration from `configfile` using YAML.
        The configuration is stored in self.data as a dictionary tree.
        
        @param configfile: the file name from which to load the configuration
        @return: True if configuration was loaded, False otherwise
        """
        if configfile is None and self.source is not None:
            # in case the configfile was not specified, take the location
            # that was set in the constructor, if any
            configfile = self.source
        if configfile is not None:
            # load the data using YAML
            cf = file(configfile, 'r')
            self.data = yaml.load(cf)
            cf.close()
            # verify that the data is a dictionary
            if type(self.data) is not dict:
                self.data = {}
            return True
        return False
    
    def save(self, configfile=None):
        """
        Function that saves the configuration to `configfile` using YAML.
        
        @param configfile: the file name in which to save the configuration
        @return: True if configuration was saved, False otherwise
        """
        if configfile is None and self.source is not None:
            # in case the configfile was not specified, take the location
            # that was set in the constructor, if any
            configfile = self.source
        if configfile is not None:
            # dump the data using YAML
            cf = file(configfile, 'w')
            yaml.dump(self.data, cf, default_flow_style=False)
            cf.close()
            return True
        return False
    
    def print_all(self):
        """
        This function dumps the configuration data to the console for
        debugging purposes. The data is formatted using YAML.
        """
        print yaml.dump(self.data, default_flow_style=False)
    
    def sections(self):
        """
        This function returns a list of sections present in the configuration.
        """
        return self.data.keys()
    
    def attributes(self, section=DEFAULT):
        """
        This function returns a list of attributes in section `section`.
        
        @param section: The section which's attributes are to be listed
        @return: The list of attributes in `section`
        """
        if section in self.data and type(self.data[section]) is dict:
            return self.data[section].keys()
        else:
            return []
    
    def get_branch(self, path=[]):
        """
        This function returns a configuration tree branch at `path`.
        
        @param path: The location of the branch to be returned
        @return: Configuration branch at `path` or None.
        """
        return walk(self.data, path)

    get = get_branch #: This function is a short form for get_branch
    
    def set(self, path, value):
        """
        This function sets a configuration attribute at `path` to `value`.
        
        @param path: The path to the attribute that is to be set to `value`
        @param value: The new value for the attribute at `path`
        @return: True if the operation was successful
        """
        tpath = list(path)
        if type(path) is list:
            element = tpath.pop()
            branch = self.data
            
            # walk the path until the parent node
            for node in tpath:
                if node not in branch or type(branch[node]) is not dict:
                    branch[node] = {}
                branch = branch[node]
            
            # see if we need to set the value or erase the attribute
            if value is not None:
                # set a new value
                branch[element] = value
            elif element in branch:
                # in case value is None, delete the attribute alltogether
                del branch[element]
            
            return True
        return False
    
    def clear(self):
        """
        This function clears the data of this Config
        """
        self.data.clear()
    
    def compare_to(self, other_config):
        """
        This function compares this Config element to another.
        
        @param other_config: An other Config (or it's subclass) element
        @return: A dictionary tree of differences
        """
        if isinstance(other_config, Config):
            return compare_trees(self.data, other_config.data)


def walk(tree, path=[]):
    """
    This function returns a branch of a dictionary tree by walking using
    the attribute names specified with `path`.
    
    @param tree: A dictionary tree
    @param path: A list of keys to be iterated until the final location
    @return: Value of `tree` at `path` or None if such path does not exist
    """
    if type(path) is list:
        branch = tree
        for node in path:
            if type(branch) is dict and node in branch:
                branch = branch[node]
            else:
                return None
        return branch
    return None

def compare_trees(a, b):
    """
    This function does an in-depth comparison of 2 dictionary trees and
    produces another tree of their differences. This function calls itself
    recursively to produce the final result.
    
    Changed and newly set attribute values are present in the result as
    their new values. Removed values and branches appear as None.
    
    @param a: Dictionary tree A
    @param b: Dictionary tree B
    @return: Differences between A and B
    """
    r = {}
    ak = set(a.keys())
    bk = set(b.keys())
    
    for key in ak.difference(bk):
        # copy each key that appears in A but not in B
        r[key] = copy.deepcopy(a[key])
    for key in bk.difference(ak):
        # investigate each key that is not present in A
        if type(b[key]) is dict:
            # if the value was a dictionary, recurse and report the result
            r[key] = compare_trees({}, b[key])
        else:
            # if it was a simple value or a list, report None
            r[key] = None
    for key in ak.intersection(bk):
        # investigate each key that appears both in A and B
        
        if type(a[key]) is dict and type(b[key]) is dict:
            # if values are dictionaries, recurse and report if they differ
            diff = compare_trees(a[key], b[key])
            if diff:
                r[key] = diff
        elif type(a[key]) is list and type(b[key]) is list:
            # if values are lists, check if they differ
            if set(a[key]).symmetric_difference(set(b[key])):
                # the lists are different, so return the value in A
                r[key] = copy.deepcopy(a[key])
        elif type(a[key]) is not type(b[key]) or a[key] != b[key]:
            # in all other cases, simply return a copy of the value in A
            r[key] = copy.deepcopy(a[key])
        
    return r

def diff_type(a, b, path):
    """
    This function reports which is the type of difference that was
    detected in `a` and `b` at `path`.
    
    @param a: Dictionary tree A
    @param b: Dictionary tree B
    @param path: Location of the difference
    @return: If the value at `path` was added in A, return CONFIG_ADDED.
        When it was removed in A, return CONFIG_REMOVED.
        Otherwise, return CONFIG_CHANGED.
    """
    a_branch = walk(a, path)
    b_branch = walk(b, path)
    
    if a_branch is None:
        return CONFIG_REMOVED
    elif b_branch is None:
        return CONFIG_ADDED
    return CONFIG_CHANGED
