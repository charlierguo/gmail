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
