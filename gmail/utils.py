

from .gmail import Gmail 

def login(username, password):
    g = Gmail()
    g.login(username, password)
    return g