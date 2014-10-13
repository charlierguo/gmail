"""
A Pythonic interface to Google's GMail, with all the tools you'll need. Search,
read and send multipart emails, archive, mark as read/unread, delete emails,
and manage labels.

Installation
############

Install using pip
::
    pip install gmail_client

Features
########

1. Search emails
2. Read emails
3. Emails: label, archive, delete, mark as read/unread/spam, star
4. Manage labels

Basic usage
###########

To start, import the `gmail_client` library.
::
    import gmail_client

Authenticating sessions
***********************

To easily get up and running:
::
    import gmail_client

    g = gmail_client.login(username, password)

Which will automatically log you into a GMail account.
This is actually a shortcut for creating a new `Gmail` object:
::
    from gmail_client import Gmail

    g = Gmail()
    g.login(username, password)
    # play with your gmail...
    g.logout()

You can also check if you are logged in at any time:
::
    g = gmail_client.login(username, password)
    g.logged_in # should be True, AuthenticationError if login fails

OAuth authentication
********************

If you have already received an `OAuth2 access token from Google <https://developers.google.com/accounts/docs/OAuth2>`_
for a given user, you can easily log the user in. (Because OAuth 1.0 usage was deprecated in April 2012, this library
does not currently support its usage).
::
    gmail = gmail_client.authenticate(username, access_token)

Filtering emails
****************

Get all messages in your inbox:
::
    g.inbox().mail()

Get messages that fit some criteria:
::
    g.inbox().mail(after=datetime.date(2013, 6, 18), before=datetime.date(2013, 8, 3))
    g.inbox().mail(on=datetime.date(2009, 1, 1)
    g.inbox().mail(sender="myfriend@gmail.com") # "from" is reserved, use "fr" or "sender"
    g.inbox().mail(to="directlytome@gmail.com")

Combine flags and options:
::
    g.inbox().mail(unread=True, sender="myboss@gmail.com")

Browsing labeled emails is similar to working with your inbox.
::
    g.mailbox('Urgent').mail()

Every message in a conversation/thread will come as a separate message.
::
    g.inbox().mail(unread=True, before=datetime.date(2013, 8, 3) sender="myboss@gmail.com")

Working with emails
*******************

**Important: calls to `mail()` will return a list of empty email messages (with unique IDs). To work with labels, headers, subjects, and bodies, call `fetch()` on an individual message. You can call mail with `prefetch=True`, which will fetch the bodies automatically.**
::
    unread = g.inbox().mail(unread=True)
    print unread[0].body # None

    unread[0].fetch()
    print unread[0].body

Mark news past a certain date as read and archive it:
::
    emails = g.inbox().mail(before=datetime.date(2013, 4, 18), sender="news@nbcnews.com")
    for email in emails:
        email.read() # can also unread(), delete(), spam(), or star()
        email.archive()

Delete all emails from a certain person:
::
    emails = g.inbox().mail(sender="junkmail@gmail.com")
    for email in emails:
        email.delete()

You can use also `label` method instead of `mailbox`:
::
    g.label("Faxes").mail()

Add a label to a message:
::
    email.add_label("Faxes")

Download message attachments:
::
    for attachment in email.attachments:
        print 'Saving attachment: ' + attachment.name
        print 'Size: ' + str(attachment.size) + ' KB'
        attachment.save('attachments/' + attachment.name)

There is also few shortcuts to mark messages quickly:
::
    email.read()
    email.unread()
    email.spam()
    email.star()
    email.unstar()

Roadmap
*******

* Write tests
* Better label support
* Moving between labels/mailboxes
* Intuitive thread fetching & manipulation
* Sending mail via Google's SMTP servers (for now, check out https://github.com/paulchakravarti/gmail-sender)


**Copyright (c) 2014 Wilberto Morales**, see LICENSE for details.

Authors
#######

This is a fork of `Charlie Guo's gmail library <https://github.com/charlierguo/>`_.
Heavily inspired by `Kriss "nu7hatch" Kowalik's GMail for Ruby library <https://github.com/nu7hatch/gmail>`_.

1. `Wilberto Morales <https://github.com/wilbertom/>`_
2. `Brian Everett Peterson <https://github.com/bepetersn/>`_

"""

__title__ = 'gmail'
__version__ = '0.1'
__author__ = 'Wilberto Morales'
__build__ = 0x0001
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2014 Wilberto Morales'

from .gmail import Gmail
from .mailbox import Mailbox 
from .message import Message, Attachment
from .exceptions import GmailException, ConnectionError, AuthenticationError


# utility methods for people to use

def login(username, password):
    gmail = Gmail()
    gmail.login(username, password)
    return gmail

def authenticate(username, access_token):
    gmail = Gmail()
    gmail.authenticate(username, access_token)
    return gmail
