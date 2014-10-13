# -*- coding: utf-8 -*-

"""

This module contains the set of Gmail's exceptions.

"""


class GmailException(RuntimeError):
    """
    The base exception in the library. Also raised when there
    was an ambiguous exception that occurred while handling a
    request.

    """

class ConnectionError(GmailException):
    """
    A Connection error occurred.

    """

class AuthenticationError(GmailException):
    """
    Gmail Authentication failed.

    """

class Timeout(GmailException):
    """
    The request timed out.

    """
