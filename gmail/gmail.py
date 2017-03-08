from email.utils import parseaddr, getaddresses
import imaplib
import itertools
import logging
import re
import smtplib
from smtplib import SMTPResponseException, SMTPServerDisconnected, SMTPAuthenticationError

from .mailbox import Mailbox
from .utf import encode as encode_utf7, decode as decode_utf7
from .exceptions import *


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


class Gmail():
    # GMail IMAP defaults
    GMAIL_IMAP_HOST = 'imap.gmail.com'
    GMAIL_IMAP_PORT = 993

    # GMail SMTP defaults
    # TODO: implement SMTP functions
    GMAIL_SMTP_HOST = "smtp.gmail.com"
    GMAIL_SMTP_PORT = 587

    def __init__(self, debug=True):
        self.username = None
        self.password = None
        self.access_token = None

        self.imap = None
        self.smtp = None
        self.logged_in = False
        self.mailboxes = {}
        self.current_mailbox = None
        self.debug = debug

        # self.connect_imap()

    def _connect_imap(self, raise_errors=True):
        # try:
        #     self.imap = imaplib.IMAP4_SSL(self.GMAIL_IMAP_HOST, self.GMAIL_IMAP_PORT)
        # except socket.error:
        #     if raise_errors:
        #         raise Exception('connect_imapion failure.')
        #     self.imap = None

        self.imap = imaplib.IMAP4_SSL(
            self.GMAIL_IMAP_HOST, self.GMAIL_IMAP_PORT)

        return self.imap

    def is_connected(self):
        """
            Check is session connected - initially by checking session instance and
            then sending NOOP to validate connection

            Sets self.session to None if connection has been closed
        """
        if self.smtp is None:
            return False
        try:
            rcode, msg = self.smtp.noop()
            if rcode == 250:
                return True
            else:
                self.smtp = None
                return False
        except (SMTPServerDisconnected, SMTPResponseException):
            self.smtp = None
            return False

    def _connect_smtp(self, raise_errors=True):

        # self.smtp = smtplib.SMTP(self.server,self.port)
        # self.smtp.set_debuglevel(self.debug)
        # self.smtp.ehlo()
        # self.smtp.starttls()
        # self.smtp.ehlo()
        self.smtp = smtplib.SMTP(self.GMAIL_SMTP_HOST, self.GMAIL_SMTP_PORT)
        self.smtp.set_debuglevel(self.debug)

        self.smtp.ehlo()
        self.smtp.starttls()
        self.smtp.ehlo()

        return self.smtp

    def fetch_mailboxes(self):
        response, mailbox_list = self.imap.list()
        if response == 'OK':
            for mailbox in mailbox_list:
                mailbox_name = mailbox.split(
                    b'"/"')[-1].replace(b'"', b'').strip()
                mailbox = Mailbox(self)
                mailbox.external_name = mailbox_name
                self.mailboxes[mailbox_name] = mailbox

        logger.debug('self.mailboxes:\n{}'.format(self.mailboxes))

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

    def _login_imap(self, username, password):

        if not self.imap:
            self._connect_imap()
        imap_login = self.imap.login(self.username, self.password)
        self.logged_in = (imap_login and imap_login[0] == 'OK')
        if self.logged_in:
            self.fetch_mailboxes()
        return self.logged_in

    def send(self, message):
        if not self.is_connected():
            self._connect_smtp()

        recepients = []
        recepients.extend(message.get_all('To') or [])
        recepients.extend(message.get_all('Bcc') or [])
        recepients.extend(message.get_all('Cc') or [])

        self.smtp.sendmail(self.username, recepients, message.as_string())

    def login(self, username, password, only_fetch=False):
        # by default logins for both IMAP and SMTP connection

        self.username = username
        self.password = password

        try:
            self._login_imap(self.username, self.password)
        except imaplib.IMAP4.error:
            raise AuthenticationError

        if not only_fetch:
            self._connect_smtp()

            try:
                self.smtp.login(self.username, self.password)

            except SMTPAuthenticationError:
                raise AuthenticationError

        return self.logged_in

    def authenticate(self, username, access_token):
        self.username = username
        self.access_token = access_token

        if not self.imap:
            self._connect_imap()

        try:
            auth_string = 'user=%s\1auth=Bearer %s\1\1' % (
                username, access_token)
            imap_auth = self.imap.authenticate(
                'XOAUTH2', lambda x: auth_string)
            self.logged_in = (imap_auth and imap_auth[0] == 'OK')
            if self.logged_in:
                self.fetch_mailboxes()
        except imaplib.IMAP4.error:
            raise AuthenticationError

        return self.logged_in

    def logout(self):
        self.imap.logout()
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
        fetch_str = ','.join(list(messages.keys()))
        response, results = self.imap.uid(
            'FETCH', fetch_str, '(BODY.PEEK[] FLAGS X-GM-THRID X-GM-MSGID X-GM-LABELS)')
        for index in range(len(results) - 1):
            raw_message = results[index]
            if re.search(r'UID (\d+)', raw_message[0]):
                uid = re.search(r'UID (\d+)', raw_message[0]).groups(1)[0]
                messages[uid].parse(raw_message)

        return messages

    def labels(self, require_unicode=False):
        keys = list(self.mailboxes.keys())
        if require_unicode:
            keys = [decode_utf7(key) for key in keys]
        return keys

    def inbox(self):
        return self.mailbox(bytes("INBOX", "ascii"))

    def spam(self):
        return self.mailbox(bytes("[Gmail]/Spam"))

    def starred(self):
        return self.mailbox(bytes("[Gmail]/Starred"))

    def all_mail(self):
        return self.mailbox(bytes("[Gmail]/All Mail"))

    def sent_mail(self):
        return self.mailbox(bytes("[Gmail]/Sent Mail"))

    def important(self):
        return self.mailbox(bytes("[Gmail]/Important"))

    def mail_domain(self):
        return self.username.split('@')[-1]
