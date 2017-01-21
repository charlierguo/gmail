import datetime
import email
import os
import re
import sys
import time
from email.encoders import encode_base64
from email.header import decode_header, make_header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate,make_msgid,getaddresses,parseaddr
from imaplib import ParseFlags
from mimetypes import guess_type

if sys.version_info[0] == 2:
    unicode_type = unicode
else:
    unicode_type = str


def charset(s):
    return  'utf-8' if isinstance(s,unicode_type) else 'us-ascii'


class Message():

    @staticmethod
    def create(subject,to,cc=None,bcc=None,text=None,is_html=False,attachments=None,sender=None,reply_to=None):
        """
        
        

        returns: MIMEMultipart or MIMEText. Currently as a SMTP message doesnt require any of the methods which 
                 are provided by this message class, this create method doesnt return a Message object.  
        """
        if not is_html and not attachments:
            # Simple plain text email
            message = MIMEText(text,'plain', charset(text))
        else:
            # Multipart message
            message = MIMEMultipart()
            if is_html:
                # Add html & plain text alernative parts
                alt = MIMEMultipart('alternative')
                alt.attach(MIMEText(text,'plain',charset(text)))
                alt.attach(MIMEText(html,'html',charset(html)))
                message.attach(alt)
            else:
                # Just add plain text part
                txt = MIMEText(text,'plain',charset(text))
                message.attach(txt)
            # Add attachments
            for a in attachments or []:
                message.attach(Message._file_to_mime_attachment(a))
        # Set headers
        message['To'] = to
        if cc: message['Cc'] = cc
        if bcc: message['Bcc'] = bcc

        if sender:
            message['From'] = sender

            if not reply_to:
                # If 'Reply-To' is not provided, set it to the 'From' value
                message['Reply-To'] = sender

        if reply_to:
            message['Reply-To'] = reply_to

        message['Subject'] = subject
        
        return message


    def __init__(self, mailbox, uid):
        self.uid = uid
        self.mailbox = mailbox
        self.gmail = mailbox.gmail if mailbox else None

        # this is the wrapped object. based on the type this can be a MimeText or MimeMultipart
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
        for hdr in list(message.keys()):
            hdrs[hdr] = message[hdr]
        return hdrs

    def parse_flags(self, headers):
        return list(ParseFlags(headers))
        # flags = re.search(r'FLAGS \(([^\)]*)\)', headers).groups(1)[0].split(' ')

    def parse_labels(self, headers):
        if re.search(r'X-GM-LABELS \(([^\)]+)\)', headers):
            labels = re.search(
                r'X-GM-LABELS \(([^\)]+)\)', headers).groups(1)[0].split(' ')
            return [l.replace('"', '').decode("string_escape") for l in labels]
        else:
            return list()

    def parse_subject(self, encoded_subject):
        dh = decode_header(encoded_subject)
        default_charset = 'ASCII'
        return ''.join([str(t[0], t[1] or default_charset) for t in dh])

    def parse(self, raw_message):
        raw_headers = raw_message[0]
        raw_email = raw_message[1]

        self.message = email.message_from_string(raw_email)
        self.headers = self.parse_headers(self.message)

        self.to = self.message['to']
        self.fr = self.message['from']
        self.delivered_to = self.message['delivered_to']

        self.subject = self.parse_subject(self.message['subject'])

        if self.message.get_content_maintype() == "multipart":
            for content in self.message.walk():
                if content.get_content_type() == "text/plain":
                    self.body = content.get_payload(decode=True)
                elif content.get_content_type() == "text/html":
                    self.html = content.get_payload(decode=True)
        elif self.message.get_content_maintype() == "text":
            self.body = self.message.get_payload()

        self.sent_at = datetime.datetime.fromtimestamp(
            time.mktime(email.utils.parsedate_tz(self.message['date'])[:9]))

        self.flags = self.parse_flags(raw_headers)

        self.labels = self.parse_labels(raw_headers)

        if re.search(r'X-GM-THRID (\d+)', raw_headers):
            self.thread_id = re.search(
                r'X-GM-THRID (\d+)', raw_headers).groups(1)[0]
        if re.search(r'X-GM-MSGID (\d+)', raw_headers):
            self.message_id = re.search(
                r'X-GM-MSGID (\d+)', raw_headers).groups(1)[0]

        # Parse attachments into attachment objects array for this message
        self.attachments = [
            Attachment(attachment) for attachment in self.message._payload
            if not isinstance(attachment, str) and attachment.get('Content-Disposition') is not None
        ]

    def fetch(self):
        if not self.message:
            response, results = self.gmail.imap.uid(
                'FETCH', self.uid, '(BODY.PEEK[] FLAGS X-GM-THRID X-GM-MSGID X-GM-LABELS)')

            self.parse(results[0])

        return self.message

    @staticmethod
    def _file_to_mime_attachment(file):
        """
            Create MIME attachment
        """
        if isinstance(file, MIMEBase):
                # Already MIME object - return
            return file
        else:
            # Assume filename - guess mime-type from extension and return MIME
            # object
            main, sub = (guess_type(file)[
                         0] or 'application/octet-stream').split('/', 1)
            attachment = MIMEBase(main, sub)
            with open(file, 'rb') as f:
                attachment.set_payload(f.read())
            attachment.add_header('Content-Disposition',
                                  'attachment', filename=os.path.basename(a))
            encode_base64(attachment)
            return attachment

    # returns a list of fetched messages (both sent and received) in
    # chronological order
    def fetch_thread(self):
        self.fetch()
        original_mailbox = self.mailbox
        self.gmail.use_mailbox(original_mailbox.name)

        # fetch and cache messages from inbox or other received mailbox
        response, results = self.gmail.imap.uid(
            'SEARCH', None, '(X-GM-THRID ' + self.thread_id + ')')
        received_messages = {}
        uids = results[0].split(' ')
        if response == 'OK':
            for uid in uids:
                received_messages[uid] = Message(original_mailbox, uid)
            self.gmail.fetch_multiple_messages(received_messages)
            self.mailbox.messages.update(received_messages)

        # fetch and cache messages from 'sent'
        self.gmail.use_mailbox('[Gmail]/Sent Mail')
        response, results = self.gmail.imap.uid(
            'SEARCH', None, '(X-GM-THRID ' + self.thread_id + ')')
        sent_messages = {}
        uids = results[0].split(' ')
        if response == 'OK':
            for uid in uids:
                sent_messages[uid] = Message(
                    self.gmail.mailboxes['[Gmail]/Sent Mail'], uid)
            self.gmail.fetch_multiple_messages(sent_messages)
            self.gmail.mailboxes[
                '[Gmail]/Sent Mail'].messages.update(sent_messages)

        self.gmail.use_mailbox(original_mailbox.name)

        # combine and sort sent and received messages
        return sorted(list(dict(list(received_messages.items()) + list(sent_messages.items())).values()), key=lambda m: m.sent_at)


class Attachment:

    def __init__(self, attachment):
        self.name = attachment.get_filename()
        # Raw file data
        self.payload = attachment.get_payload(decode=True)
        # Filesize in kilobytes
        self.size = int(round(len(self.payload) / 1000.0))

    def save(self, path=None):
        if path is None:
            # Save as name of attachment if there is no path specified
            path = self.name
        elif os.path.isdir(path):
            # If the path is a directory, save as name of attachment in that
            # directory
            path = os.path.join(path, self.name)

        with open(path, 'wb') as f:
            f.write(self.payload)
