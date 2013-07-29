import datetime
import email
import re
import time

class Message():


    def __init__(self, mailbox, uid):
        self.uid = uid
        self.mailbox = mailbox
        self.gmail = mailbox.gmail if mailbox else None

        self.message = None

        self.subject = None
        self.body = None

        self.to = None
        self.fr = None
        self.cc = None
        self.delivered_to = None

        self.sent_at = None

        self.thread_id = None
        self.message_id = None


    def parse(self, raw_message, raw_flags, raw_body):
        raw_headers = raw_message[0]
        raw_email = raw_message[1]

        self.message = email.message_from_string(raw_email)

        self.subject = self.message['subject']
        self.to = self.message['to']
        self.fr = self.message['fr']
        self.delivered_to = self.message['delivered_to']
        self.body = body
        self.sent_at = datetime.datetime.fromtimestamp(time.mktime(email.utils.parsedate_tz(self.message['date'])[:9]))

        if re.search(r'X-GM-THRID (\d+)', gm_headers):
            self.thread_id = re.search(r'X-GM-THRID (\d+)', gm_headers).groups(1)
        if re.search(r'X-GM-MSGID (\d+)', gm_headers):
            self.message_id = re.search(r'X-GM-MSGID (\d+)', gm_headers).groups(1)

    def fetch(self):
        if not self.message:
            response, results = self.gmail.connection().uid('FETCH', self.uid, '(RFC822.PEEK X-GM-THRID X-GM-MSGID X-GM-LABELS)')
            
            self.parse(results[0], results[1][0], results[1][1])

        return self.message

