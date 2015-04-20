#!/usr/bin/python
#coding:utf-8


from mana_message import Email, SMS

import mana_log
LOG = mana_log.GetLog(__name__)

import  mana_conf
CONF = mana_conf.GetConf()

from mana_public import ALARM_QUEUE

def alarm():
    LOG.info("Begin to alarm thread")
    while True:
        if not ALARM_QUEUE.empty():
            msg_body = ALARM_QUEUE.get()
            _alarm(msg_body)


def _alarm(msg_body):
    try:
        message = 'Region:%s,Instance_ID:%s,Instance_Name:%s,Project:%s,User:%s,AlarmBody:%s,Device:%s,data:%s%s'\
                    %(msg_body.region, msg_body.instance_id, msg_body.instance_name, msg_body.project, msg_body.user, \
                      msg_body.alarm_obj, msg_body.device_name, msg_body.max_data, msg_body.unit)
        LOG.info(message)
        send_email(msg_body)
        send_phone_message(msg_body)
    except Exception,e:
        LOG.error(e)

def send_email(msg_body):
    email_host = CONF.get('email_host')
    email_port = CONF.get('email_port')
    sender = CONF.get('email_sender')
    sender_pwd = CONF.get('email_sender_pwd')
    receivers = CONF.get('email_receiver')
    try:
        msg = "报警模块:%s<br> 异常数据值:%s%s<br>报警区域:%s<br>主机名:%s<br>主机id:%s<br>所属项目:%s<br>所属用户:%s<br>设备名称:%s<br>"\
                    %(msg_body.alarm_obj, msg_body.max_data, msg_body.unit, msg_body.region, msg_body.instance_name,\
                      msg_body.instance_id, msg_body.project, msg_body.user, msg_body.device_name)
        subject = '星云监控报警' 
        emailclient = Email(email_host, email_port, sender, sender_pwd)
        for receiver  in receivers:
            emailclient.sendmsg(receiver, subject, msg)
    except Exception,e:
        LOG.error(e)

def send_phone_message(msg_body):
    phone_host = CONF.get('phone_host')
    phone_port = CONF.get('phone_port')
    gametype=CONF.get('phone_gametype')
    priority=CONF.get('phone_priority')
    acttype=CONF.get('phone_acttype')
    receivers=CONF.get('phone_receiver')
    try:
        msg = "报警模块:%s,区域:%s,项目:%s,名称:%s,数据:%s%s"%(msg_body.alarm_obj, msg_body.region,\
                msg_body.project, msg_body.device_name, msg_body.max_data, msg_body.unit)
        for receiver in receivers:
            smsclient = SMS(phone_host, phone_port, gametype, priority, acttype)
            smsclient.sendmsg(receiver, msg)
    except Exception,e:
        LOG.error(e)


if __name__ == "__main__":
    alarm()
