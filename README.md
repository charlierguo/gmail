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

    g.inbox().emails(after=datetime.Date(2013, 6, 18), before=datetime.Date(2013, 8, 3))
    g.inbox().emails(on=datetime.Date(2009, 1, 1)
    g.inbox().emails(fr="myfriend@gmail.com") # "from" is reserved, use "fr" or "sender"
    g.inbox().emails(to="directlytome@gmail.com")

Combine flags and options:

    g.inbox.count(unread=True, from="myboss@gmail.com")
    
Browsing labeled emails is similar to work with inbox.

    g.mailbox('Urgent').emails()
    
Getting messages works the same way as counting: Remember that every message in a 
conversation/thread will come as a separate message.

    g.inbox.emails(:unread, :before => Date.parse("2010-04-20"), :from => "myboss@gmail.com")
    
### Working with emails! (NOT IMPLEMENTED)

Any news older than 4-20, mark as read and archive it:

    gmail.inbox.find(:before => Date.parse("2010-04-20"), :from => "news@nbcnews.com").each do |email|
      email.read! # can also unread!, spam! or star!
      email.archive!
    end

Delete emails from X:

    gmail.inbox.find(:from => "x-fiance@gmail.com").each do |email|
      email.delete!
    end

Save all attachments in the "Faxes" label to a local folder:

    folder = "/where/ever"
    gmail.mailbox("Faxes").emails.each do |email|
      if !email.message.attachments.empty?
        email.message.save_attachments_to(folder)
      end
    end
     
You can use also `#label` method instead of `#mailbox`: 

    gmail.label("Faxes").emails {|email| ... }

Save just the first attachment from the newest unread email (assuming pdf):

    email = gmail.inbox.find(:unread).first
    email.attachments[0].save_to_file("/path/to/location")

Add a label to a message:

    email.label("Faxes")
    
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

