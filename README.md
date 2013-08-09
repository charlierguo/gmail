# GMail for Python

A Pythonic interface to Google's GMail, with all the tools you'll need. Search, 
read and send multipart emails, archive, mark as read/unread, delete emails, 
and manage labels.

__This library is still under development, so please forgive some of the rough edges__

Heavily inspired by Kriss "nu7hatch" Kowalik's GMail for Ruby library (https://github.com/nu7hatch/gmail)

## Author

* Charlie Guo [https://github.com/charlierguo]

## Installation

For now, installation is manual (`pip` support not yet implemented):

    git clone git://github.com/charlierguo/gmail.git

## Features

* Search emails
* Read emails 
* Emails: label, archive, delete, mark as read/unread/spam, star
* Manage labels

## Basic usage

To start, import the `gmail` library.

```python
import gmail
```
    
### Authenticating gmail sessions

To easily get up and running:

```python
import gmail 

g = gmail.login(username, password)
```

Which will automatically log you into a GMail account. 
This is actually a shortcut for creating a new Gmail object:

```python
from gmail import Gmail

g = Gmail()
g.login(username, password)
# play with your gmail...
g.logout()
```

You can also check if you are logged in at any time:

```python
g = gmail.login(username, password)
g.logged_in # Should be True, AuthenticationError if login fails
```

### OAuth authentication 

If you have already received an OAuth2 access token from Google (https://developers.google.com/accounts/docs/OAuth2) for a given user, you can easily log the user in. (Because OAuth 1.0 usage was deprecated in April 2012, this library does not currently support its usage)

```python
gmail = gmail.authenticate(username, access_token)
```

### Filtering emails
    
Get all messages in your inbox:

```python
g.inbox().mail()
```

Get messages that fit some criteria:

```python
g.inbox().mail(after=datetime.date(2013, 6, 18), before=datetime.date(2013, 8, 3))
g.inbox().mail(on=datetime.date(2009, 1, 1))
g.inbox().mail(fr="myfriend@gmail.com") # "from" is reserved, use "fr" or "sender"
g.inbox().mail(to="directlytome@gmail.com")
```

Combine flags and options:

```python
g.inbox().mail(unread=True, from="myboss@gmail.com")
```
    
Browsing labeled emails is similar to working with your inbox.

```python
g.mailbox('Urgent').mail()
```
    
Every message in a conversation/thread will come as a separate message.

```python
g.inbox().mail(unread=True, before=datetime.date(2013, 8, 3) from="myboss@gmail.com")
```
    
### Working with emails

__Important: calls to `mail()` will return a list of empty email messages (with unique IDs). To work with labels, headers, subjects, and bodies, call `fetch()` on an individual message. You can call mail with `prefetch=True`, which will fetch the bodies automatically.__

```python
unread = g.inbox().mail(unread=True)
print unread[0].body
# None

unread[0].fetch()
print unread[0].body
# Dear ...,
```

Mark news past a certain date as read and archive it:

```python
emails = g.inbox().mail(before=datetime.date(2013, 4, 18), from="news@nbcnews.com")
for email in emails:
    email.read() # can also unread(), delete(), spam(), or star()
    email.archive()
```

Delete all emails from a certain person:

```python
emails = g.inbox().mail(from="junkmail@gmail.com")
for email in emails:
    email.delete()
```
     
You can use also `label` method instead of `mailbox`: 

```python
g.label("Faxes").mail()
```

Add a label to a message:

```python
email.add_label("Faxes")
```
    
There is also few shortcuts to mark messages quickly:

```python
email.read()
email.unread()
email.spam()
email.star()
email.unstar()
```

### Roadmap
* Write tests
* Better label support
* Moving between labels/mailboxes
* Intuitive thread fetching & manipulation
* Sending mail via Google's SMTP servers (for now, check out https://github.com/paulchakravarti/gmail-sender)

## Copyright

* Copyright (c) 2013 Charlie Guo

See LICENSE for details.

