import re
import imaplib
import smtplib

from mailbox import Mailbox
from utf import encode as encode_utf7, decode as decode_utf7
from exceptions import *

# For SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Charset
from email.header import Header
from email.generator import Generator
from email import Encoders
from os.path import basename

class Gmail():
    # GMail IMAP defaults
    GMAIL_IMAP_HOST = 'imap.gmail.com'
    GMAIL_IMAP_PORT = 993

    # GMail SMTP defaults
    GMAIL_SMTP_HOST = "smtp.gmail.com"
    GMAIL_SMTP_PORT = 587

    def __init__(self):
        self.username = None
        self.password = None
        self.access_token = None

        self.imap = None
        self.smtp = None
        self.logged_in = False
        self.mailboxes = {}
        self.current_mailbox = None

    def connect(self, raise_errors=True):
        self.imap = imaplib.IMAP4_SSL(self.GMAIL_IMAP_HOST, self.GMAIL_IMAP_PORT)
        self.smtp = smtplib.SMTP(self.GMAIL_SMTP_HOST, self.GMAIL_SMTP_PORT)
        # self.smtp.set_debuglevel(self.debug)
        self.smtp.ehlo()
        self.smtp.starttls()

    def fetch_mailboxes(self):
        response, mailbox_list = self.imap.list()
        if response == 'OK':
            for mailbox in mailbox_list:
                mailbox_name = mailbox.split('"/"')[-1].replace('"', '').strip()
                mailbox = Mailbox(self)
                mailbox.external_name = mailbox_name
                self.mailboxes[mailbox_name] = mailbox

    def use_mailbox(self, mailbox):
        if mailbox:
            self.imap.select(mailbox)
        self.current_mailbox = mailbox

    def mailbox(self, mailbox_name):
        if mailbox_name not in self.mailboxes:
            mailbox_name = encode_utf7(mailbox_name)
        mailbox = self.mailboxes.get(mailbox_name)

        if mailbox and not self.current_mailbox == mailbox_name:
            self.use_mailbox(mailbox_name)

        return mailbox

    def create_mailbox(self, mailbox_name):
        mailbox = self.mailboxes.get(mailbox_name)
        if not mailbox:
            self.imap.create(mailbox_name)
            mailbox = Mailbox(self, mailbox_name)
            self.mailboxes[mailbox_name] = mailbox

        return mailbox

    def delete_mailbox(self, mailbox_name):
        mailbox = self.mailboxes.get(mailbox_name)
        if mailbox:
            self.imap.delete(mailbox_name)
            del self.mailboxes[mailbox_name]

    def login(self, username, password):
        self.username = username
        self.password = password

        if not self.imap:
            self.connect()

        try:
            imap_login = self.imap.login(self.username, self.password)
            smtp_login = self.smtp.login(self.username, self.password)

            self.logged_in = (imap_login and imap_login[0] == 'OK' and smtp_login)
            if self.logged_in:
                self.fetch_mailboxes()
        except:
            raise AuthenticationError

        return self.logged_in

    def authenticate(self, username, access_token):
        self.username = username
        self.access_token = access_token

        if not self.imap:
            self.connect()

        try:
            auth_string = 'user=%s\1auth=Bearer %s\1\1' % (username, access_token)
            imap_auth = self.imap.authenticate('XOAUTH2', lambda x: auth_string)
            self.logged_in = (imap_auth and imap_auth[0] == 'OK')
            if self.logged_in:
                self.fetch_mailboxes()
        except imaplib.IMAP4.error:
            raise AuthenticationError

        return self.logged_in

    def logout(self):
        self.imap.logout()
        self.smtp.close()
        self.logged_in = False

    def label(self, label_name):
        return self.mailbox(label_name)

    def find(self, mailbox_name="[Gmail]/All Mail", **kwargs):
        box = self.mailbox(mailbox_name)
        return box.mail(**kwargs)
    
    def copy(self, uid, to_mailbox, from_mailbox=None):
        if from_mailbox:
            self.use_mailbox(from_mailbox)
        self.imap.uid('COPY', uid, to_mailbox)

    def fetch_multiple_messages(self, messages):
        fetch_str =  ','.join(messages.keys())
        response, results = self.imap.uid('FETCH', fetch_str, '(BODY.PEEK[] FLAGS X-GM-THRID X-GM-MSGID X-GM-LABELS)')
        for index in xrange(len(results) - 1):
            raw_message = results[index]
            if re.search(r'UID (\d+)', raw_message[0]):
                uid = re.search(r'UID (\d+)', raw_message[0]).groups(1)[0]
                messages[uid].parse(raw_message)

        return messages

    def labels(self, require_unicode=False):
        keys = self.mailboxes.keys()
        if require_unicode:
            keys = [decode_utf7(key) for key in keys]
        return keys

    def inbox(self):
        return self.mailbox("INBOX")

    def spam(self):
        return self.mailbox("[Gmail]/Spam")

    def starred(self):
        return self.mailbox("[Gmail]/Starred")

    def all_mail(self):
        return self.mailbox("[Gmail]/All Mail")

    def sent_mail(self):
        return self.mailbox("[Gmail]/Sent Mail")

    def important(self):
        return self.mailbox("[Gmail]/Important")

    def mail_domain(self):
        return self.username.split('@')[-1]

    def noop(self):
        return self.imap.noop()

    def add_files(self, message, attachment):
        for filename in attachment:
            try:
                file_handle = open(filename, "rb")
            except:
                file_handle = None

            if file_handle == None:
				continue

            content = file_handle.read()
            attach_part = MIMEBase('application', 'octet-stream')
            attach_part.set_payload(content)
            Encoders.encode_base64(attach_part)
            attach_part.add_header('Content-Disposition',
                'attachment; filename="%s"' % basename(filename))

            message.attach(attach_part)
            file_handle.close()

    def send_mail(self, recipient, subject, body, attachment):
        recipient = recipient if type(recipient) is list else [recipient]
        attachment = attachment if type(attachment) is list else [attachment]

        # For unicode message
        message = MIMEMultipart('alternative')
        message['Subject'] = "%s" % Header(subject, 'utf-8')
        message['From'] = "%s" % (Header(self.username, 'utf-8'))

        recipient_string = ""
        for name in recipient:
            recipient_string = recipient_string + name + ","
        # Cut the last comma
        recipient_string = recipient_string[0: len(recipient_string) - 1]

        message['To'] = "%s" % (Header(recipient_string, 'utf-8'))
        message.add_header('reply-to', "%s" % (Header(self.username, 'utf-8')))

        # Attach text and attachment parts
        text_part = MIMEText(body, 'plain', 'UTF-8')
        message.attach(text_part)
        self.add_files(message, attachment)

        self.smtp.sendmail(self.username, recipient, message.as_string())
