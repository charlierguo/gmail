import datetime
import email
import re
import time
from imaplib import ParseFlags
from utf import encode, decode

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

        self.flags = []
        self.labels = []

        self.thread_id = None
        self.message_id = None


    def is_read(self):
        return ('\\Seen' in self.flags)

    def read(self):
        flag = '\\Seen'
        self.gmail.connection().uid('STORE', self.uid, '+FLAGS', flag)
        if flag not in self.flags: self.flags.append(flag)

    def unread(self):
        flag = '\\Seen'
        self.gmail.connection().uid('STORE', self.uid, '-FLAGS', flag)
        if flag in self.flags: self.flags.remove(flag)

    def is_starred(self):
        return ('\\Flagged' in self.flags)

    def star(self):
        flag = '\\Flagged'
        self.gmail.connection().uid('STORE', self.uid, '+FLAGS', flag)
        if flag not in self.flags: self.flags.append(flag)

    def unstar(self):
        flag = '\\Flagged'
        self.gmail.connection().uid('STORE', self.uid, '-FLAGS', flag)
        if flag in self.flags: self.flags.remove(flag)

    def is_deleted(self):
        return ('\\Deleted' in self.flags)

    def delete(self):
        flag = '\\Deleted'
        self.gmail.connection().uid('STORE', self.uid, '+FLAGS', flag)
        if flag not in self.flags: self.flags.append(flag)

    def undelete(self):
        flag = '\\Deleted'
        self.gmail.connection().uid('STORE', self.uid, '-FLAGS', flag)
        if flag in self.flags: self.flags.remove(flag)

    def is_draft(self):
        return ('\\Draft' in self.flags)

    def has_label(self, label):
        full_label = '\\%s' % label
        return (full_label in self.labels)

    def add_label(self, label):
        full_label = '\\%s' % label
        self.gmail.connection().uid('STORE', self.uid, '+X-GM-LABELS', full_label)
        if full_label not in self.labels: self.labels.append(full_label)

    def remove_label(self, label):
        full_label = '\\%s' % label
        self.gmail.connection().uid('STORE', self.uid, '-X-GM-LABELS', full_label)
        if full_label in self.labels: self.labels.remove(full_label)





    def parse_flags(self, headers):
        return list(ParseFlags(headers))
        # flags = re.search(r'FLAGS \(([^\)]*)\)', headers).groups(1)[0].split(' ')

    def parse_labels(self, headers):
        if re.search(r'X-GM-LABELS \(([^\)]+)\)', headers):
            labels = re.search(r'X-GM-LABELS \(([^\)]+)\)', headers).groups(1)[0].split(' ')
            return map(lambda l: l.replace('"', '').decode("string_escape"), labels)
        else:
            return list()

    def parse(self, raw_message):
        raw_headers = raw_message[0]
        raw_email = raw_message[1]

        # print raw_headers

        self.message = email.message_from_string(raw_email)

        self.to = self.message['to']
        self.fr = self.message['fr']
        self.delivered_to = self.message['delivered_to']

        self.subject = self.message['subject']
        if self.message.get_content_maintype() == "multipart":
            for content in self.message.walk():       
                if content.get_content_type() == "text/plain":
                    self.body = content.get_payload(decode=True)
        elif self.message.get_content_maintype() == "text":
            self.body = self.message.get_payload()

        self.sent_at = datetime.datetime.fromtimestamp(time.mktime(email.utils.parsedate_tz(self.message['date'])[:9]))

        self.flags = self.parse_flags(raw_headers)
        # print self.flags
        self.labels = self.parse_labels(raw_headers)
        # print self.labels

        if re.search(r'X-GM-THRID (\d+)', raw_headers):
            self.thread_id = re.search(r'X-GM-THRID (\d+)', raw_headers).groups(1)[0]
        if re.search(r'X-GM-MSGID (\d+)', raw_headers):
            self.message_id = re.search(r'X-GM-MSGID (\d+)', raw_headers).groups(1)[0]

    def fetch(self):
        if not self.message:
            response, results = self.gmail.connection().uid('FETCH', self.uid, '(BODY.PEEK[] FLAGS X-GM-THRID X-GM-MSGID X-GM-LABELS)')

            self.parse(results[0])

        return self.message

