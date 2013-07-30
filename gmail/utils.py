

from .gmail import Gmail 

def login(username, password):
    g = Gmail()
    g.login(username, password)
    return g

def authenticate(username, access_token):
    g = Gmail()
    g.authenticate(username, access_token)
    return g