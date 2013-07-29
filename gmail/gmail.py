import imaplib
from mailbox import Mailbox
from exceptions import AuthenticationError

class Gmail():
    # GMail IMAP defaults
    GMAIL_IMAP_HOST = 'imap.gmail.com'
    GMAIL_IMAP_PORT = 993

    # GMail SMTP defaults
    # TODO: implement SMTP functions
    GMAIL_SMTP_HOST = "smtp.gmail.com"
    GMAIL_SMTP_PORT = 587

    def __init__(self, options={}):
        defaults = {}
        self.username = None
        self.password = None

        self.options = defaults.update(options)

        self.imap = None
        self.logged_in = False
        self.mailboxes = {}
        self.current_mailbox = None

        # self.connect()

    def connect(self, raise_errors=True):
        # print 'connecting...'
        # try:
        #     self.imap = imaplib.IMAP4_SSL(self.GMAIL_IMAP_HOST, self.GMAIL_IMAP_PORT)
        # except socket.error:
        #     if raise_errors:
        #         raise Exception('Connection failure.')
        #     self.imap = None

        self.imap = imaplib.IMAP4_SSL(self.GMAIL_IMAP_HOST, self.GMAIL_IMAP_PORT)

        return self.imap

    def connection(self):
        return self.imap

    def switch_to_mailbox(self, mailbox):
        if mailbox:
            # TODO: utf-7 encode mailbox name
            self.connection().select(mailbox)
        self.current_mailbox = mailbox

    def mailbox(self, name):
        # TODO: test mailbox
        name = str(name)
        mailbox = self.mailboxes.get(name) or Mailbox(self, name)
        self.mailboxes[name] = mailbox
        if not self.current_mailbox == name:
            self.switch_to_mailbox(name)

        return mailbox

    def mailboxes(self):
        return self.mailboxes

    def fetch_mailboxes(self):
        response, mailbox_list = self.connection().list()
        if response == 'OK':
            for mailbox in mailbox_list:
                mailbox_name = mailbox.split(' ')[-1].replace('"', '')
                self.mailboxes[mailbox_name] = Mailbox(self, mailbox_name)

    def login(self, username, password):
        self.username = username
        self.password = password

        if not self.connection():
            self.connect()

        try:
            imap_login = self.connection().login(self.username, self.password)
            self.logged_in = (imap_login and imap_login[0] == 'OK')
            if self.logged_in:
                self.fetch_mailboxes()
        except imaplib.IMAP4.error:
            if raise_errors:
                raise AuthenticationError

        return self.logged_in

    def authenticate(self, username, auth_token):
        # TODO: implement authenticate
        return

    def logout(self):
        self.connection().logout()

    def labels(self):
        return


    def compose(self, mail):
        # TODO: implement compose
        return

    def deliver(self, mail, raise_errors):
        # TODO: implement deliver
        return

    def inbox(self):
        return self.mailbox("INBOX")

    def spam(self):
        return self.mailbox("[Gmail]/Spam")

    def starred(self):
        return self.mailbox("[Gmail]/Starred")

    def all_mail(self):
        return self.mailbox("[Gmail]/All Mail")

    def mail_domain(self):
        return self.username.split('@')[-1]
