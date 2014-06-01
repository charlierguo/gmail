import datetime
import email
import re
import time
import os

from email.header import decode_header, HeaderParseError
from imaplib import ParseFlags


def try_parse(header, encoding="ASCII"):
    """
    Try to parse specified header using specified encoding.
    On failure to do so, use ISO-8859-1, and then UTF-8.
    Header and encoding are most often return from decode_header (but use try_decode instead of decode_header, see below).
    """
    if encoding is None:
        encoding = 'ASCII'

    try:
        return unicode(header, encoding)
    except (UnicodeDecodeError, LookupError):
        try:
            return unicode(header, 'ISO-8859-1')
        except UnicodeDecodeError:
            return unicode(header, 'UTF-8')


def try_decode(header):
    """
    Try to decode specified header,
    We need to wrap this in a try / except for the very rare case of FUCKED UP clients
    using FUCKING non-standard base63 encoding. Wow. Such smart. Fucking faglords.
    Please phpmailer.codeworxtech.com fix this shit or i'll fucking kill your family and set your house on fire.
    See http://bugs.python.org/issue12489
    """

    try:
        return decode_header(header)
    except HeaderParseError:
        return [[header, None]]


class Message():
    def __init__(self, mailbox, uid):
        self.uid = uid
        self.mailbox = mailbox
        self.gmail = mailbox.gmail if mailbox else None

        self.message = None
        self.headers = {}

        self.subject = None
        self.body = None
        self.html = None

        self.to = None
        self.fr = None
        self.cc = None
        self.delivered_to = None

        self.sent_at = None

        self.flags = []
        self.labels = []

        self.thread_id = None
        self.thread = []
        self.message_id = None

        self.attachments = None

    def is_read(self):
        return ('\\Seen' in self.flags)

    def read(self):
        flag = '\\Seen'
        self.gmail.imap.uid('STORE', self.uid, '+FLAGS', flag)
        if flag not in self.flags:
            self.flags.append(flag)

    def unread(self):
        flag = '\\Seen'
        self.gmail.imap.uid('STORE', self.uid, '-FLAGS', flag)
        if flag in self.flags:
            self.flags.remove(flag)

    def is_starred(self):
        return ('\\Flagged' in self.flags)

    def star(self):
        flag = '\\Flagged'
        self.gmail.imap.uid('STORE', self.uid, '+FLAGS', flag)
        if flag not in self.flags:
            self.flags.append(flag)

    def unstar(self):
        flag = '\\Flagged'
        self.gmail.imap.uid('STORE', self.uid, '-FLAGS', flag)
        if flag in self.flags:
            self.flags.remove(flag)

    def is_draft(self):
        return ('\\Draft' in self.flags)

    def has_label(self, label):
        full_label = '%s' % label
        return (full_label in self.labels)

    def add_label(self, label):
        full_label = '%s' % label
        self.gmail.imap.uid('STORE', self.uid, '+X-GM-LABELS', full_label)
        if full_label not in self.labels:
            self.labels.append(full_label)

    def remove_label(self, label):
        full_label = '%s' % label
        self.gmail.imap.uid('STORE', self.uid, '-X-GM-LABELS', full_label)
        if full_label in self.labels:
            self.labels.remove(full_label)

    def is_deleted(self):
        return ('\\Deleted' in self.flags)

    def delete(self):
        flag = '\\Deleted'
        self.gmail.imap.uid('STORE', self.uid, '+FLAGS', flag)
        if flag not in self.flags:
            self.flags.append(flag)

        trash = '[Gmail]/Trash' if '[Gmail]/Trash' in self.gmail.labels() else '[Gmail]/Bin'
        if self.mailbox.name not in ['[Gmail]/Bin', '[Gmail]/Trash']:
            self.move_to(trash)

    # def undelete(self):
    #     flag = '\\Deleted'
    #     self.gmail.imap.uid('STORE', self.uid, '-FLAGS', flag)
    #     if flag in self.flags: self.flags.remove(flag)

    def move_to(self, name):
        self.gmail.copy(self.uid, name, self.mailbox.name)
        if name not in ['[Gmail]/Bin', '[Gmail]/Trash']:
            self.delete()

    def archive(self):
        self.move_to('[Gmail]/All Mail')

    def parse_headers(self, message):
        hdrs = {}
        for hdr in message.keys():
            hdrs[hdr] = message[hdr]
        return hdrs

    def parse_flags(self, headers):
        return list(ParseFlags(headers))
        # flags = re.search(r'FLAGS \(([^\)]*)\)', headers).groups(1)[0].split(' ')

    def parse_labels(self, headers):
        if re.search(r'X-GM-LABELS \(([^\)]+)\)', headers):
            labels = re.search(r'X-GM-LABELS \(([^\)]+)\)', headers).groups(1)[0].split(' ')
            return map(lambda l: l.replace('"', '').decode("string_escape"), labels)
        else:
            return list()

    def parse_header(self, encoded_header):
        dh = try_decode(encoded_header)
        return ''.join([try_parse(t[0], t[1]) for t in dh])

    def parse(self, raw_message):
        raw_headers = raw_message[0]
        raw_email = raw_message[1]

        self.message = email.message_from_string(raw_email)

        self.headers = self.parse_headers(self.message)

        self.to = self.parse_header(self.message['to'])
        self.fr = self.parse_header(self.message['from'])
        self.subject = self.parse_header(self.message['subject'])

        if self.message.get_content_maintype() == "multipart":
            for content in self.message.walk():
                if content.get_content_type() == "text/plain":
                    self.body = try_parse(content.get_payload(decode=True), content.get_content_charset())
                elif content.get_content_type() == "text/html":
                    self.html = try_parse(content.get_payload(decode=True), content.get_content_charset())
        elif self.message.get_content_maintype() == "text":
            if self.message.get_content_type() == "text/plain":
                self.body = try_parse(self.message.get_payload(decode=True), self.message.get_content_charset())
            elif self.message.get_content_type() == "text/html":
                self.html = try_parse(self.message.get_payload(decode=True), self.message.get_content_charset())
        try:
            self.sent_at = datetime.datetime.fromtimestamp(time.mktime(email.utils.parsedate_tz(self.message['date'])[:9]))
        except:
            self.sent_at = datetime.datetime.now()

        self.flags = self.parse_flags(raw_headers)

        self.labels = self.parse_labels(raw_headers)

        if re.search(r'X-GM-THRID (\d+)', raw_headers):
            self.thread_id = re.search(r'X-GM-THRID (\d+)', raw_headers).groups(1)[0]
        if re.search(r'X-GM-MSGID (\d+)', raw_headers):
            self.message_id = re.search(r'X-GM-MSGID (\d+)', raw_headers).groups(1)[0]

        # Parse attachments into attachment objects array for this message
        self.attachments = [
            Attachment(attachment) for attachment in self.message._payload
                if not isinstance(attachment, basestring) and attachment.get('Content-Disposition') is not None and attachment.get_filename() is not None
        ]

    def fetch(self):
        if not self.message:
            response, results = self.gmail.imap.uid('FETCH', self.uid, '(BODY.PEEK[] FLAGS X-GM-THRID X-GM-MSGID X-GM-LABELS)')

            self.parse(results[0])

        return self.message

    # returns a list of fetched messages (both sent and received) in chronological order
    def fetch_thread(self):
        self.fetch()
        original_mailbox = self.mailbox
        self.gmail.use_mailbox(original_mailbox.name)

        # fetch and cache messages from inbox or other received mailbox
        response, results = self.gmail.imap.uid('SEARCH', None, '(X-GM-THRID ' + self.thread_id + ')')
        received_messages = {}
        uids = results[0].split(' ')
        if response == 'OK':
            for uid in uids:
                received_messages[uid] = Message(original_mailbox, uid)
            self.gmail.fetch_multiple_messages(received_messages)
            self.mailbox.messages.update(received_messages)

        # fetch and cache messages from 'sent'
        self.gmail.use_mailbox('[Gmail]/Sent Mail')
        response, results = self.gmail.imap.uid('SEARCH', None, '(X-GM-THRID ' + self.thread_id + ')')
        sent_messages = {}
        uids = results[0].split(' ')
        if response == 'OK':
            for uid in uids:
                sent_messages[uid] = Message(self.gmail.mailboxes['[Gmail]/Sent Mail'], uid)
            self.gmail.fetch_multiple_messages(sent_messages)
            self.gmail.mailboxes['[Gmail]/Sent Mail'].messages.update(sent_messages)

        self.gmail.use_mailbox(original_mailbox.name)

        # combine and sort sent and received messages
        return sorted(dict(received_messages.items() + sent_messages.items()).values(), key=lambda m: m.sent_at)


class Attachment:
    def __init__(self, attachment):
        try:
            dh = try_decode(attachment.get_filename())
            self.name = ''.join([try_parse(t[0], t[1]) for t in dh])
        except UnicodeEncodeError:
            self.name = attachment.get_filename()

        # Raw file data
        if isinstance(attachment.get_payload(), basestring):
            self.payload = attachment.get_payload(decode=True)
            # Filesize in kilobytes
            self.size = int(round(len(self.payload) / 1000.0))
        else:
            # Special case. Seems to occurs only for EML attachments.
            self.payload = None
            self.size = None

    def save(self, path=None):
        if path is None:
            # Save as name of attachment if there is no path specified
            path = self.name
        elif os.path.isdir(path):
            # If the path is a directory, save as name of attachment in that directory
            path = os.path.join(path, self.name)

        with open(path, 'wb') as f:
            f.write(self.payload)
