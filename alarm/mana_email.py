#! /usr/bin/python
#coding:utf-8

import smtplib
from email.mime.text import MIMEText
from email.header import Header

#import mana_conf
#CONF = mana_conf.GetConf()

#EMAIL_HOST = 'mail.ztgame.com'
#EMAIL_PORT = 25

#SENDER = 'yangwanyuan@ztgame.com'
#SENDER_PW = 'ywy8861@000'


import mana_log
LOG = mana_log.GetLog(__name__)

#import logging 
#LOG = logging.getLogger(__name__)

class Email():
    def __init__(self, email_host, email_port, email_sender, email_sender_pwd):
        self.email_host = email_host
        self.email_port = email_port
        self.sender = email_sender
        self.sender_pw = email_sender_pwd


    def sendmsg(self, receiver, subject, msg):
        try:
            self.handle = smtplib.SMTP(self.email_host, self.email_port)
            self.handle.login(self.sender, self.sender_pw)
            msgbody = MIMEText('<html><h1>%s</h1></html>'%msg, 'html', 'utf-8')
            msgbody["Accept-Language"]= "zh-CN"
            msgbody["Accept-Charset"]= "ISO-8859-1,utf-8"
            msgbody['Subject'] = Header(subject, 'utf-8')
            self.handle.sendmail(self.sender, receiver, msgbody.as_string())
            LOG.info("send message %s to receiver %s success " %(subject, receiver))
        except Exception, e:
            print e;

    def __del__(self):
        if self.handle:
            self.handle.close()       



if __name__ == "__main__":
    EMAIL_HOST = 'mail.ztgame.com'
    EMAIL_PORT = 25

    #SENDER = 'yangwanyuan@ztgame.com'
    #SENDER_PW = 'ywy8861@000'

    SENDER = 'autowork@ztgame.com'
    SENDER_PW = 'ak123$%^'
    emailclient = Email(EMAIL_HOST, EMAIL_PORT, SENDER, SENDER_PW)
    msg = u'msg:你好啊 !!!'
    subject = u'subject: hello world!!'
    receiver = 'yangwanyuan@ztgame.com'
    emailclient.sendmsg(receiver, subject, msg)

