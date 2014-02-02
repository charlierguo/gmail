from message import Message
from utf import encode as encode_utf7, decode as decode_utf7


class Mailbox():

    def __init__(self, gmail, name="INBOX"):
        self.name = name
        self.gmail = gmail
        self.date_format = "%d-%b-%Y"
        self.messages = {}

    @property
    def external_name(self):
        if "external_name" not in vars(self):
            vars(self)["external_name"] = encode_utf7(self.name)
        return vars(self)["external_name"]

    @external_name.setter
    def external_name(self, value):
        if "external_name" in vars(self):
            del vars(self)["external_name"]
        self.name = decode_utf7(value)

    def mail(self, prefetch=False, **kwargs):
        search = ['ALL']

        kwargs.get('read')   and search.append('SEEN')
        kwargs.get('unread') and search.append('UNSEEN')

        kwargs.get('starred')   and search.append('FLAGGED')
        kwargs.get('unstarred') and search.append('UNFLAGGED')

        kwargs.get('deleted')   and search.append('DELETED')
        kwargs.get('undeleted') and search.append('UNDELETED')

        kwargs.get('draft')   and search.append('DRAFT')
        kwargs.get('undraft') and search.append('UNDRAFT')

        kwargs.get('before') and search.extend(['BEFORE', kwargs.get('before').strftime(self.date_format)])
        kwargs.get('after')  and search.extend(['SINCE', kwargs.get('after').strftime(self.date_format)])
        kwargs.get('on')     and search.extend(['ON', kwargs.get('on').strftime(self.date_format)])

        kwargs.get('header') and search.extend(['HEADER', kwargs.get('header')[0], kwargs.get('header')[1]])

        kwargs.get('sender') and search.extend(['FROM', kwargs.get('sender')])
        kwargs.get('fr') and search.extend(['FROM', kwargs.get('fr')])
        kwargs.get('to') and search.extend(['TO', kwargs.get('to')])
        kwargs.get('cc') and search.extend(['CC', kwargs.get('cc')])

        kwargs.get('subject') and search.extend(['SUBJECT', kwargs.get('subject')])
        kwargs.get('body') and search.extend(['BODY', kwargs.get('body')])

        kwargs.get('label') and search.extend(['X-GM-LABELS', kwargs.get('label')])
        kwargs.get('attachment') and search.extend(['HAS', 'attachment'])

        kwargs.get('query') and search.extend([kwargs.get('query')])

        emails = []
        # print search
        response, data = self.gmail.imap.uid('SEARCH', *search)
        if response == 'OK':    
            uids = filter(None, data[0].split(' ')) # filter out empty strings

            for uid in uids:
                if not self.messages.get(uid):
                    self.messages[uid] = Message(self, uid)
                emails.append(self.messages[uid])

            if prefetch and emails:
                messages_dict = {}
                for email in emails:
                    messages_dict[email.uid] = email
                self.messages.update(self.gmail.fetch_multiple_messages(messages_dict))

        return emails

    # WORK IN PROGRESS. NOT FOR ACTUAL USE
    def threads(self, prefetch=False, **kwargs):
        emails = []
        response, data = self.gmail.imap.uid('SEARCH', 'ALL')
        if response == 'OK':    
            uids = data[0].split(' ') 


            for uid in uids:
                if not self.messages.get(uid):
                    self.messages[uid] = Message(self, uid)
                emails.append(self.messages[uid])

            if prefetch:
                fetch_str = ','.join(uids)
                response, results = self.gmail.imap.uid('FETCH', fetch_str, '(BODY.PEEK[] FLAGS X-GM-THRID X-GM-MSGID X-GM-LABELS)')
                for index in xrange(len(results) - 1):
                    raw_message = results[index]
                    if re.search(r'UID (\d+)', raw_message[0]):
                        uid = re.search(r'UID (\d+)', raw_message[0]).groups(1)[0]
                        self.messages[uid].parse(raw_message)

        return emails

    def count(self, **kwargs):
        return len(self.mail(**kwargs))

    def cached_messages(self):
        return self.messages
