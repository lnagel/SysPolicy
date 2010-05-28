# SysPolicy
# 
# Copyright (c) 2010 Lenno Nagel
# Author: Lenno Nagel <lenno-at-nagel.ee>
# URL: <http://trac.syspolicy.org>
# Released under the GNU General Public License version 3

"""
Functions for prompting the user for choices and passwords
"""

import string
import crypt
import getpass
from random import choice
from _cracklib import FascistCheck

SALT_TYPE = 6 #: 1: MD5, 2a: Blowfish, 5: SHA-256, 6: SHA-512
SALT_SIZE = 16 #: maximum value: 16 characters
PASSWORD_SIZE = 10 #: default password size if no policy is given

class AbortedException(Exception):
    """
    This exception is raised when user aborts a yes/no confirmation dialog.
    """
    pass

def confirm(text, default=True):
    """
    Get a confirmation from the user using the provided prompting text.
    Additionally, a default value can be specified which is returned when the 
    user simply presses Return. The default value is also highlighted in the
    prompt.
    
    When the user wishes to quit instead, an AbortedException is raised.
    """
    options = ""
    if default == True:
        options = "Y/n/q"
    elif default == False:
        options = "y/N/q"
    
    responses = {'': default, 
        'y': True, 
        'n': False}
    
    while True:
        input = raw_input(text + " [" + options + "] ")
        if input in responses:
            return responses[input]
        elif input == 'q':
            raise AbortedException()
        else:
            print "Sorry, response", input, "not understood."

def getstr(text, default=''):
    """
    Function for prompting a string value from the user on the command line.
    
    Additionally, a default value can be specified in case the user simply
    presses Return on the prompt. The default value will be shown in brackets.
    """
    prompt = text + ' '
    if default != '':
        prompt += '[' + default + '] '
    input = raw_input(prompt)
    if input != '':
        return input
    else:
        return default

def genpass(size=PASSWORD_SIZE):
    """
    Generate a random password from lower- and uppercase letters and digits of
    exactly size characters in length.
    """
    pool = string.letters + string.digits
    return ''.join([choice(pool) for i in range(size)])

def checkpass(password, policy={}):
    """
    Check if the given password meets a certain security policy. There are
    initial checks made on the length of the password and the amount of
    different character classes it contains.
    
    Additionally, the password is checked using the cracklib library.
    """
    minlen = policy.get('minlen', PASSWORD_SIZE) #: minimum length
    minclass = policy.get('minclass', 0) #: min number of character classes
    dcredit = policy.get('dcredit', 1) #: max credit for digits
    ucredit = policy.get('ucredit', 1) #: max credit for uppercase characters
    lcredit = policy.get('lcredit', 1) #: max credit for lowercase characters
    ocredit = policy.get('ocredit', 1) #: max credit for other characters
    
    dcount = 0 #: digit count
    ucount = 0 #: uppercase characters count
    lcount = 0 #: lowercase characters count
    ocount = 0 #: other characters count
    ccount = 0 #: character classes count
    bonus = 0 #: bonus credits awarded
    
    # count the characters of different classes
    for c in password:
        if c in string.digits:
            dcount += 1
        elif c in string.ascii_lowercase:
            lcount += 1
        elif c in string.ascii_uppercase:
            ucount += 1
        else:
            ocount += 1
    
    # count the character classes and award bonus credits
    for (credit, count) in [(dcredit, dcount), (ucredit, ucount),
                            (lcredit, lcount), (ocredit, ocount)]:
        # count char classes that have been seen at least once
        ccount += min(1, count)
        # add up to credit or count amount of bonus points per class
        bonus += min(credit, count)
    
    if ccount < minclass:
        raise ValueError('not enough different character classes')
    
    if (len(password) + bonus) < minlen:
        raise ValueError('it is too short')

    # if no exception was raised until now, cracklib will give the final answer
    return FascistCheck(password)

def setpwd(policy={}):
    """
    This function performs a password prompting routine with the user.
    
    It accepts a password strenght policy as an argument, and based on 
    this a default password will be proposed with the chance of setting
    a custom one.
    
    The custom password will be subjected to strenght checks using 
    the built-in strenght checker and also the cracklib library.
    """
    # extract the size information from the policy
    size = policy.get('minlen', PASSWORD_SIZE)
    size -= policy.get('minclass', 0)
    
    # generate a password salt and a default password
    salt = "$%d$%s$" % (SALT_TYPE, genpass(SALT_SIZE))
    default = genpass(size)
    
    print "The auto-generated password is '"+default+"'."
    print "Password policy:", policy
    
    # try to prompt the user for a password
    try:
        input = getpass.getpass("Accept default or enter another: ")
        
        # while the user is trying to enter a password
        while len(input) > 0:
            try:
                # check if the password meets the policy requirements
                if checkpass(input, policy):
                    if input == getpass.getpass("Repeat password: "):
                        # return the password in crypt(..) format
                        return crypt.crypt(input, salt)
                    else:
                        raise ValueError("the passwords don't match")
            except Exception, e:
                print "Invalid password:", e
            
            input = getpass.getpass("Enter new password: ")
    except EOFError:
        pass
    
    # in case the user didn't enter a custom password, return the default
    print "Accepted default"
    return crypt.crypt(default, salt)
