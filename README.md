# GMail for Python

A Pythonic interface to Google's GMail, with all the tools you'll need. Search, 
read and send multipart emails, archive, mark as read/unread, delete emails, 
and manage labels.

Heavily inspired by Kriss "nu7hatch" Kowalik's GMail for Ruby library (https://github.com/nu7hatch/gmail)

## Author(s)

* Charlie Guo [https://github.com/charlierguo]

## Installation

You can install it easy using pip:

    sudo pip install gmail
    
Or install it manually:

    git clone git://github.com/charlierguo/gmail.git
    cd gmail
    python setup.py

## Features

* Search emails
* Read emails (handles attachments)
* Emails: label, archive, delete, mark as read/unread/spam, star
* Manage labels

## Basic usage

First of all import the `gmail` library.

    import gmail
    
### Authenticating gmail sessions

This will you automatically log in to your account. 
    
    import gmail

    g = gmail.Gmail()
    g.login(username, password)
    # play with your gmail...
    g.logout()

There is a shortcut to avoid creating a new Gmail object
    
    import gmail 

    g = gmail.login(username, password)

You can also check if you are logged in at any time:

    g = gmail.login(username, password)
    g.logged_in # Should be True

### XOAuth authentication (NOT IMPLEMENTED)

### Gathering emails
    
Get messages in your inbox:

    g.inbox().emails()

Get messages with some criteria:

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

Any news older than 4-20, mark as read and archive it:

    emails = g.inbox().mail(before=datetime.Date(2013, 4, 20), from="news@nbcnews.com")
    for email in emails:
        email.read() # can also unread(), delete(), spam(), or star()
        email.archive()


Delete emails from X:

    gmail.inbox.find(:from => "ex@gmail.com").each do |email|
      email.delete!
    end
     
You can use also `#label` method instead of `#mailbox`: 

    g.label("Faxes").mail()

Add a label to a message:

    email.add_label("Faxes")
    
Example above will raise error when you don't have the `Faxes` label. You can 
avoid this using:

    email.label!("Faxes") # The `Faxes` label will be automatically created now

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

## Note on Patches/Pull Requests
 
* Fork the project.
* Make your feature addition or bug fix.
* Add tests for it. This is important so I don't break it in a
  future version unintentionally.
* Commit, do not mess with version, or history.
  (if you want to have your own version, that is fine but bump version in a commit by itself I can ignore when I pull)
* Send me a pull request. Bonus points for topic branches.

## Copyright

* Copyrignt (c) 2013 Charlie Guo

See LICENSE for details.

