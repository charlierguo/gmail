# -*- coding: utf-8 -*-

"""
gmail.exceptions
~~~~~~~~~~~~~~~~~~~

This module contains the set of Gmails' exceptions.

"""


class GmailException(RuntimeError):
    """There was an ambiguous exception that occurred while handling your
    request."""

class ConnectionError(GmailException):
    """A Connection error occurred."""

class AuthenticationError(GmailException):
    """Gmail Authentication failed."""

class Timeout(GmailException):
    """The request timed out."""
