import smtplib
from email.mime.text import MIMEText
from email.header import Header

EMAIL_HOST = 'mail.ztgame.com'
EMAIL_PORT = 25

SENDER = 'yangwanyuan@ztgame.com'
SENDER_PW = 'ywy8861@000'


import mana_log
LOG = mana_log.GetLog(__name__)

#import logging 
#LOG = logging.getLogger(__name__)

class Email():
    def __init__(self):
        self.email_host = EMAIL_HOST 
        self.email_port = EMAIL_PORT
        self.sender = SENDER
        self.sender_pw = SENDER_PW


    def sendmsg(self, receiver, subject, msg):
        try:
            self.handle = smtplib.SMTP(self.email_host, self.email_port)
            self.handle.login(self.sender, self.sender_pw)
            msgbody = MIMEText('<html><h1>%s</h1></html>'%msg, 'html', 'utf-8')
            msgbody['Subject'] = Header(subject, 'utf-8')
            self.handle.sendmail(self.sender, receiver, msgbody.as_string())
            LOG.info("send message to receiver success")
        except Exception, e:
            print e;

    def __del__(self):
        if self.handle:
            self.handle.close()       



if __name__ == "__main__":
    emailclient = Email()
    msg = 'msg: hello world!!!'
    subject = 'subject: hello world!!'
    receiver = SENDER
    emailclient.sendmsg(receiver, subject, msg)

