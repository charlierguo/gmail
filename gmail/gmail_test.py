import os
import gmail

email = os.environ["GMAIL_ADDR"]
password = os.environ["GMAIL_PASSWORD"]


def test_smtp_login():
    gm = gmail.Gmail()
    gm.connect_smtp()
    gm.login_smtp(email,password)

    