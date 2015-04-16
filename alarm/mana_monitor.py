#!/usr/bin/python
#coding:utf-8

import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

import os
import time

import simplejson

from mana_http import HttpCon, UrlCon
from mana_message import Email, SMS

import mana_log
LOG = mana_log.GetLog(__name__)

import  mana_conf
CONF = mana_conf.GetConf()

unit_map = {
            'cpu_util':{"%":1},
            'network_incoming_bytes_rate':  {
                                            "B/s":1,
                                            "KB/s":1024, 
                                            "MB/s":1024*1024,
                                            "GB/s":1024*1024*1024
                                            },
            'network_outgoing_bytes_rate':  {
                                            "B/s":1,
                                            "KB/s":1024, 
                                            "MB/s":1024*1024,
                                            "GB/s":1024*1024*1024
                                            },
            'disk_write_bytes_rate':        {
                                            "B/s":1,
                                            "KB/s":1024, 
                                            "MB/s":1024*1024,
                                            "GB/s":1024*1024*1024
                                            },
            'disk_read_bytes_rate':          {
                                            "B/s":1,
                                            "KB/s":1024, 
                                            "MB/s":1024*1024,
                                            "GB/s":1024*1024*1024
                                            },
            'network_incoming_bytes':       {
                                            "B":1,
                                            "KB":1024, 
                                            "MB":1024*1024,
                                            "GB":1024*1024*1024
                                            }, 
            'network_outgoing_bytes':        {
                                            "B":1,
                                            "KB":1024, 
                                            "MB":1024*1024,
                                            "GB":1024*1024*1024
                                            },                   
}

class msg_item:
    def __init__(self, alarm_obj = None, instance_id = None, instance_name = None,\
                 project = None, user = None, device_name = None, max_data = None, \
                 unit = None, region = None):
        self.alarm_obj = alarm_obj
        self.instance_id = instance_id
        self.instance_name = instance_name
        self.project = project
        self.user = user
        self.device_name = device_name
        self.max_data = max_data
        self.unit = unit
        self.region = region


def run():
    interval = CONF.get('cycletime')
    LOG.info("begin to monitor,every %s seconds" %interval)
    while True:
        try:
            time_pre = time.time()
            monitor()
            time_now = time.time()
            monitor_time = time_now - time_pre
            LOG.info("this cycle monitor all instances use time: %ss" %monitor_time)
            time.sleep(interval + time_pre - time_now)
        except Exception, e:
            LOG.error(e)

def monitor():
    try:
        regions = CONF.get('regions')
        for region in regions:
            instances = get_instances_from_api(region)
            for instance in instances:
                _monitor(region, instance)
    except Exception, e:
        LOG.error(e)

def _monitor(region, instance):
    try:
        for (alarm_obj, thd) in CONF.get('alarm_list'):
            instance_id = instance.get('instance_id')
            datas = get_datas_from_api(region, instance_id, alarm_obj)
            threshold = float(thd)
            for data in datas:
                alarm(instance, data, alarm_obj, threshold, region)
    except Exception, e:
        LOG.error(e) 

def get_instances_from_api(region):
    url = CONF.get('url').get('get_all_instance_url') %region
    api_host = CONF.get('api_host')
    api_port = CONF.get('api_port')
    try:
        httpclient = HttpCon(api_host, api_port, url, "GET")
        body = httpclient.get()
        if body:
            instances = simplejson.loads(body).get('data')
    except Exception, e:
        LOG.error(e)
        return NULL
    return instances 

def get_datas_from_api(region, instance, alarm_obj):
    url = CONF.get('url').get('get_metric') %(region, alarm_obj, instance)
    api_host = CONF.get('api_host')
    api_port = CONF.get('api_port')
    try:
        httpclient = HttpCon(api_host, api_port, url, "POST")
        body = httpclient.get()
        if body:
            data = simplejson.loads(body)
    except Exception, e:
        LOG.error(e)
        return NULL
    return data


def alarm(instance, data, alarm_obj, threshold, region):
    try:
        bodys = data.get('data')
        if bodys == []:
            return False

        device_name = data.get('name')
        instance_id =instance.get('instance_id')
        instance_name = instance.get('instance_name')
        try:
            project = instance.get('project').encode('utf-8')
        except Exception:
            project = instance.get('project')
        try:
            user = instance.get('user').encode('utf-8')
        except Exception:
            user = instance.get('user')  

        for body in bodys:
            unit = body.get('unit')
            #multiple = unit_map.get(alarm_obj).get(unit)
            multiple = 1
            max_data = body.get('max') * multiple
            if max_data >  threshold:
                if unit == 'B/s':
                    max_data = round((max_data / (1024 * 1024)), 2) 
                    unit = 'MB|s'
                msg_body = msg_item(alarm_obj, instance_id, instance_name, project, user, device_name, max_data, unit, region)
                _alarm(msg_body)
                return True
    except Exception, e:
        LOG.error(e)

def _alarm(msg_body):
    try:
        message = 'Region:%s\n Instance_ID:%s\n Instance_Name:%s\n Project:%s\n User:%s\n AlarmBody:%s\n Device:%s\n Message:data is to high %s %s\n'\
                    %(msg_body.region, msg_body.instance_id, msg_body.instance_name, msg_body.project, msg_body.user, msg_body.alarm_obj,\
                      msg_body.device_name, msg_body.max_data, msg_body.unit)
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
        msg = ' Region:%s\n Instance_ID:%s\n Instance_Name:%s\n Project:%s\n User:%s\n AlarmBody:%s\n Device:%s\n Message:data is to high %s %s\n'\
                    %(msg_body.region, msg_body.instance_id, msg_body.instance_name, msg_body.project, msg_body.user, msg_body.alarm_obj,\
                      msg_body.device_name, msg_body.max_data, msg_body.unit)
        subject = msg_body.alarm_obj +  '  alarm!!!' 
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
        msg = "报警模块:%s,区域:%s,项目:%s,名称:%s,数据:%s%s" %(msg_body.alarm_obj, msg_body.region, msg_body.device_name, msg_body.project, msg_body.max_data, msg_body.unit)
        for receiver in receivers:
            smsclient = SMS(phone_host, phone_port, gametype, priority, acttype)
            smsclient.sendmsg(receiver, msg)
    except Exception,e:
        LOG.error(e)



if __name__ == "__main__":
    run()
