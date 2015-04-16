#! /usr/bin/python
#coding:utf-8

import smtplib
from email.mime.text import MIMEText
from email.header import Header


from mana_http import UrlCon
import urllib

import mana_log
LOG = mana_log.GetLog(__name__)


class Email():
    def __init__(self, email_host = None, email_port = None, email_sender = None, email_sender_pwd = None):
        self.email_host = email_host
        self.email_port = email_port
        self.sender = email_sender
        self.sender_pw = email_sender_pwd


    def sendmsg(self, receiver, subject, msg):
        try:
            self.handle = smtplib.SMTP(self.email_host, self.email_port)
            self.handle.login(self.sender, self.sender_pw)
            msgbody = MIMEText("<a>%s</a>"%msg, 'html', 'utf-8')
            msgbody["Accept-Language"]= "zh-CN"
            msgbody["Accept-Charset"]= "ISO-8859-1,utf-8"
            msgbody['Subject'] = Header(subject, 'utf-8')
            self.handle.sendmail(self.sender, receiver, msgbody.as_string())
            LOG.info("send email %s to receiver %s success " %(subject, receiver))
        except Exception, e:
            print e;

    def __del__(self):
        if self.handle:
            self.handle.close()       


class SMS():
    def __init__(self, phone_host = None, phone_port = None, gametype = None, priority = None, acttype = None):
        self.phone_host = phone_host
        self.phone_port = phone_port
        self.gametype = gametype
        self.priority = priority
        self.acttype = acttype

    def sendmsg(self, receiver, message):
        message = message.decode('utf-8').encode('gbk')
        #msg_postfix = "%A1%BE%BE%DE%C8%CB%CD%F8%C2%E7%A1%BF"
        msg_postfix = '【巨人网络】'
        msg_postfix = msg_postfix.decode('utf-8').encode('gbk')
        msg = urllib.quote(message + msg_postfix)
        url = "/emaysendMsg?dest_mobile=%s&msg_content=%s&priority=%s&gametype=%s&acttype=%s" \
              %(receiver, msg, self.priority, self.gametype, self.acttype)
        urlclient = UrlCon(self.phone_host, self.phone_port, url, "GET")
        body = urlclient.get()
        if body == '0|':
            LOG.info("send short message to receiver %s success "%receiver)
        else:
            LOG.error("send short message to receiver %s failed! return code is %s" %(receiver, body))
 
    def __del__(self):
        pass




if __name__ == "__main__":
    EMAIL_HOST = 'mail.ztgame.com'
    EMAIL_PORT = 25
    SENDER = 'autowork@ztgame.com'
    SENDER_PW = 'ak123$%^'
    email_receiver = 'yangwanyuan@ztgame.com'
    subject = u'subject: hello world!!'
    msg = u'msg:你好啊 !!!'
    emailclient = Email(EMAIL_HOST, EMAIL_PORT, SENDER, SENDER_PW)
    emailclient.sendmsg(email_receiver, subject, msg)

    #PHONE_HOST = '192.168.39.120'
    #PHONE_PORT = 29997
    #GAMETYPE = '2'
    #PRIORITY = '5'
    #ACTTYPE = '89'
    #sms_receiver = '18505532175'
    #msg = "报警模块:network,区域:beijing,名称:aaa,项目:大主宰,用户:admin"
    #smsclient = SMS(PHONE_HOST, PHONE_PORT, GAMETYPE, PRIORITY, ACTTYPE)
    #smsclient.sendmsg(sms_receiver, msg)