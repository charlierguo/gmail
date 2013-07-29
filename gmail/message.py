import datetime
import email
import re
import time

class Message():


    def __init__(self, mailbox, uid):
        self.uid = uid
        self.mailbox = mailbox
        self.gmail = mailbox.gmail if mailbox else None

        self._message = None

        self._subject = None
        self._to = None
        self._sender = None
        self._delivered_to = None
        self._body = None

        self._sent_at = None

        self._thread_id = None
        self._message_id = None

    def subject(self):
        return self._subject

    def body(self):
        return self._body

    def sender(self):
        return self._sender

    def to(self):
        return self._to

    def delivered_to(self):
        return self._delivered_to

    def sent_at(self):
        return self._sent_at

    def uid(self):
        return self.uid 

    def fetch(self):
        if not self._message:
            print 'fetching message %s...' % self.uid
            response, full_message = self.gmail.connection().uid('FETCH', self.uid, '(RFC822 BODY.PEEK[TEXT] X-GM-THRID X-GM-MSGID X-GM-LABELS)')
            

            raw_email = full_message[0][1]
            gm_headers = full_message[0][0]
            flags = full_message[1][0]
            body = full_message[1][1]
            self._message = email.message_from_string(raw_email)

            self._subject = self._message['subject']
            self._to = self._message['to']
            self._sender = self._message['sender']
            self._delivered_to = self._message['delivered_to']
            self._body = body
            self._sent_at = datetime.datetime.fromtimestamp(time.mktime(email.utils.parsedate_tz(self._message['date'])[:9]))

            if re.search(r'X-GM-THRID (\d+)', gm_headers):
                self._thread_id = re.search(r'X-GM-THRID (\d+)', gm_headers).groups(1)
            if re.search(r'X-GM-MSGID (\d+)', gm_headers):
                self._message_id = re.search(r'X-GM-MSGID (\d+)', gm_headers).groups(1)


        return self._message

