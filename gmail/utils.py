

from .gmail import Gmail 

def login(username, password):
    gmail = Gmail()
    gmail.login(username, password)
    return gmail

def authenticate(username, access_token):
    gmail = Gmail()
    gmail.authenticate(username, access_token)
    return gmail