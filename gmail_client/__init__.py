

"""

GMail! Woo!

"""

__title__ = 'gmail'
__version__ = '0.1'
__author__ = 'Charlie Guo'
__build__ = 0x0001
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2013 Charlie Guo'

from .gmail import Gmail
from .mailbox import Mailbox 
from .message import Message 
from .exceptions import GmailException, ConnectionError, AuthenticationError


# Utility methods for people to use

def login(username, password):
    gmail = Gmail()
    gmail.login(username, password)
    return gmail

def authenticate(username, access_token):
    gmail = Gmail()
    gmail.authenticate(username, access_token)
    return gmail