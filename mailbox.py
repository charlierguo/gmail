from message import Message
from utils import encode as encode_utf7

class Mailbox():

    MAILBOX_ALIASES = {
      'all'         : ['ALL'],
      'seen'        : ['SEEN'],
      'unseen'      : ['UNSEEN'],
      'read'        : ['SEEN'],
      'unread'      : ['UNSEEN'],
      'flagged'     : ['FLAGGED'],
      'unflagged'   : ['UNFLAGGED'],
      'starred'     : ['FLAGGED'],
      'unstarred'   : ['UNFLAGGED'], 
      'deleted'     : ['DELETED'],
      'undeleted'   : ['UNDELETED'],
      'draft'       : ['DRAFT'],
      'undrafted'   : ['UNDRAFT']
    }

    def __init__(self, gmail, name="INBOX"):
        self.name = name
        # TODO: utf-7 encode mailbox name
        self.external_name = encode_utf7(name)
        self.gmail = gmail
        self.messages = {}

    def emails(self, category='all', prefetch=False, **kwargs):
        search = list(self.MAILBOX_ALIASES[category])

        if kwargs.get('after'):
            search.extend(['SINCE', kwargs.get('after').strftime("%d-%B-%Y")])
        if kwargs.get('before'):
            search.extend(['BEFORE', kwargs.get('before').strftime("%d-%B-%Y")])
        if kwargs.get('on'):
            search.extend(['ON', kwargs.get('on').strftime("%d-%B-%Y")])
        if kwargs.get('sender'):
            search.extend(['FROM', kwargs.get('sender')])
        if kwargs.get('to'):
            search.extend(['TO', kwargs.get('to')])
        if kwargs.get('subject'):
            search.extend(['SUBJECT', kwargs.get('subject')])
        if kwargs.get('label'):
            search.extend(['LABEL', kwargs.get('label')])
        if kwargs.get('attachment'):
            search.extend(['HAS', 'attachment'])
        if kwargs.get('search'):
            search.extend(['BODY', kwargs.get('search')])
        if kwargs.get('body'):
            search.extend(['BODY', kwargs.get('body')])
        if kwargs.get('query'):
            search.extend([kwargs.get('query')])

        # mailbox = self.gmail.mailbox(self.name)
        # @gmail.conn.uid_search(search).collect do |uid| 

        emails = []
        response, data = self.gmail.connection().uid('SEARCH', *search)
        if response == 'OK':     
            uids = data[0].split(' ')
            for uid in uids:
                if not self.messages.get(uid):
                    self.messages[uid] = Message(self, uid)
                emails.append(self.messages[uid])

            if prefetch:
                msgs = self.gmail.connection().uid('FETCH', ','.join(uids), '(RFC822 BODY.PEEK[TEXT] X-GM-THRID X-GM-MSGID X-GM-LABELS)')
                print msgs



        return emails


    def count(*args):
        return len(self.emails(*args))

    def cached_messages():
        return self.messages
