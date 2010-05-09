
import string
from random import choice
import crypt
import getpass

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
    if len(input) >= size:
        if input == getpass.getpass("Repeat password: "):
            return password

    print "Accepted default"
    return crypt.crypt(default, salt)
