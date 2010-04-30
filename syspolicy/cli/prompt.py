
class AbortedException(Exception):
    pass

def confirm(text, default = True):
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
