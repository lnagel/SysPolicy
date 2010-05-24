
import string
from random import choice
import crypt
import getpass
import string
from _cracklib import FascistCheck

SALT_TYPE = 6
SALT_SIZE = 16
PASSWORD_SIZE = 10

class AbortedException(Exception):
    pass

def confirm(text, default=True):
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
    prompt = text + ' '
    if default != '':
        prompt += '[' + default + '] '
    input = raw_input(prompt)
    if input != '':
        return input
    else:
        return default

def genpass(size=PASSWORD_SIZE):
    pool = string.letters + string.digits
    return ''.join([choice(pool) for i in range(size)])

def checkpass(password, policy={}):
    minlen = policy.get('minlen', PASSWORD_SIZE)
    minclass = policy.get('minclass', 0)
    dcredit = policy.get('dcredit', 1)
    ucredit = policy.get('ucredit', 1)
    lcredit = policy.get('lcredit', 1)
    ocredit = policy.get('ocredit', 1)
    
    dcount = 0
    ucount = 0
    lcount = 0
    ocount = 0
    ccount = 0
    bonus = 0
    
    for c in password:
        if c in string.digits:
            dcount += 1
        elif c in string.ascii_lowercase:
            lcount += 1
        elif c in string.ascii_uppercase:
            ucount += 1
        else:
            ocount += 1
    
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

    return FascistCheck(password)

def setpwd(policy={}):
    size = policy.get('minlen', PASSWORD_SIZE)
    size -= policy.get('minclass', 0)
    salt = "$%d$%s$" % (SALT_TYPE, genpass(SALT_SIZE))
    default = genpass(size)
    
    print "The auto-generated password is '"+default+"'."
    print "Salt: ", salt
    print policy
    input = getpass.getpass("Accept or enter another: ")
    password = crypt.crypt(input, salt)
    if checkpass(input, policy):
        if input == getpass.getpass("Repeat password: "):
            return password

    print "Accepted default"
    return crypt.crypt(default, salt)
