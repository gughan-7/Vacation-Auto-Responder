import random
import time
from email import message_from_bytes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from imaplib import IMAP4_SSL
from email.utils import make_msgid
import datetime
import getpass

user = input("Enter email id: ")
password = getpass.getpass()
smtp_server = 'smtp.gmail.com'
smtp_port = 587

from_address = user
body = '''
Hello,

I am unable to reply to your email as I am away on a vacation.
I will get back to you as soon as possible

Regards,
Gughan R
'''

imap = IMAP4_SSL('imap.gmail.com')
imap.login(user, password)

server = smtplib.SMTP(smtp_server, smtp_port)
server.connect('smtp.gmail.com', '587')
server.ehlo()
server.starttls()
server.login(user, password)

def construct_mail(email):
    mail = MIMEMultipart('alternative')
    mail['Message-ID'] = make_msgid()
    mail['References'] = mail['In-Reply-To'] = email['Message-ID']
    mail['Subject'] = 'Re: ' + email['Subject']
    mail['From'] = from_address
    mail['To'] = email['Reply-To'] or email['From']
    mail.attach(MIMEText(body, 'plain'))
    return mail

def send_reply(mail):
    imap.select(readonly=True)
    _, data = imap.fetch(mail, '(RFC822)')
    imap.close()
    x = message_from_bytes(data[0][1])
    server.sendmail(from_address, [x['From']],construct_mail(x).as_bytes())
    log = 'Replied to “%s”' % (x['From'])
    print(log)
    imap.select(readonly=False)
    imap.store(mail_number, '+FLAGS', '\\Answered')
    imap.store(mail_number, '+FLAGS', '\\Seen')
    imap.close()

start_date = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
print("Auto Responder Starting")
while(True):
    imap.select(readonly=False)
    _, data = imap.search(None, f'(UNSEEN) SINCE "{start_date.strftime("%d-%b-%Y")}" UNANSWERED')
    imap.close()
    for mail_number in data[0].split():
        print(mail_number)
        imap.select()
        # _, threads = imap.search(None, f'(HEADER "In-Reply-To" "{mail_number}")')
        # print(threads)
        send_reply(mail_number)
        imap.select()
        imap.store(mail_number, '+X-GM-LABELS', '"TEST"')
        imap.copy(mail_number, '"[Gmail]/TEST"')
    interval = random.randint(45, 120)
    print("Auto Responder will run again in "+ str(interval)+" seconds")
    time.sleep(interval)