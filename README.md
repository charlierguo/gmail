# GMail for Python

A Pythonic interface to Google's GMail, with all the tools you'll need. Search, 
read and send multipart emails, archive, mark as read/unread, delete emails, 
and manage labels.

Heavily inspired by Kriss "nu7hatch" Kowalik's GMail for Ruby library (https://github.com/nu7hatch/gmail)

## Author(s)

* Charlie Guo [https://github.com/charlierguo]

## Installation

You install it manually (pip support not yet implemented):

    git clone git://github.com/charlierguo/gmail.git
    cd gmail
    python setup.py

## Features

* Search emails
* Read emails 
* Emails: label, archive, delete, mark as read/unread/spam, star
* Manage labels

## Basic usage

First of all import the `gmail` library.

    import gmail
    
### Authenticating gmail sessions

To easily get up and running:

    import gmail 

    g = gmail.login(username, password)

Which will automatically log you into a GMail account. 
This is actually a shortcut for creating a new Gmail object:
    
    import gmail

    g = gmail.Gmail()
    g.login(username, password)
    # play with your gmail...
    g.logout()

You can also check if you are logged in at any time:

    g = gmail.login(username, password)
    g.logged_in # Should be True

### OAuth authentication 

If you have already received an OAuth2 access token from Google (https://developers.google.com/accounts/docs/OAuth2) for a given user, you can easily log the user in. (Because OAuth 1.0 usage was deprecated in April 2012, this library does not currently support its usage)

    gmail = gmail.authenticate(username, access_token)

### Filtering emails
    
Get all messages in your inbox:

    g.inbox().mail()

Get messages that fit some criteria:

    g.inbox().mail(after=datetime.Date(2013, 6, 18), before=datetime.Date(2013, 8, 3))
    g.inbox().mail(on=datetime.Date(2009, 1, 1)
    g.inbox().mail(fr="myfriend@gmail.com") # "from" is reserved, use "fr" or "sender"
    g.inbox().mail(to="directlytome@gmail.com")

Combine flags and options:

    g.inbox().mail(unread=True, from="myboss@gmail.com")
    
Browsing labeled emails is similar to work with inbox.

    g.mailbox('Urgent').mail()
    
Remember that every message in a conversation/thread will come as a separate message.

    g.inbox().mail(unread=True, before=datetime.Date(2013, 8, 3) from="myboss@gmail.com")
    
### Working with emails!

Any news older than 4-18, mark as read and archive it:

    emails = g.inbox().mail(before=datetime.Date(2013, 4, 18), from="news@nbcnews.com")
    for email in emails:
        email.read() # can also unread(), delete(), spam(), or star()
        email.archive()


Delete emails from X:

    emails = g.inbox().mail(from="junkmail@gmail.com")
    for email in emails:
        email.delete()
     
You can use also `label` method instead of `mailbox`: 

    g.label("Faxes").mail()

Add a label to a message:

    email.add_label("Faxes")

You can also move message to a label/mailbox:
 
    email.move_to("Faxes")
    email.move_to!("NewLabel")
    
There is also few shortcuts to mark messages quickly:

    email.read()
    email.unread()
    email.spam()
    email.star()
    email.unstar()

### Managing labels (NOT IMPLEMENTED)

## Copyright

* Copyrignt (c) 2013 Charlie Guo

See LICENSE for details.

