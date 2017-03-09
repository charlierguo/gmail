import os
import gmail

email = os.environ["GMAIL_ADDR"]
password = os.environ["GMAIL_PASSWORD"]
to = os.environ["GMAIL_TO"]


def test_smtp_login():
    gm = gmail.Gmail()
    gm._connect_smtp()
    gm.smtp.login(email, password)


def test_smtp_send_text_email():
    gm = gmail.Gmail()

    gm.login(email, password)
    message = gmail.Message.create("Hello", to, text="Hello world")
    gm.send(message)


def test_get_inbox_email():
    gm = gmail.Gmail()
    gm.login(email, password)

    inbox = gm.inbox()
    assert inbox is not None

    inbox_email = inbox.mail()


def test_that_emails_have_content():
    gm = gmail.Gmail()
    gm.login(email, password)

    emails = gm.inbox().mail()
    assert len(emails) > 0

    first_email = emails[0]
    assert first_email.subject is not None
    assert first_email.body is not None

