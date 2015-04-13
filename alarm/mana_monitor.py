#!/usr/bin/python
#coding:utf-8


import os
import time

#import httplib
import simplejson

from mana_http import HttpCon
from mana_email import Email
#import timer 

import mana_log
LOG = mana_log.GetLog(__name__)

#import logging 

#LOG_FILE = 'monitor.log'
#logging.basicConfig(filename = os.path.join(os.getcwd(), LOG_FILE), level = logging.DEBUG) 
#LOG = logging.getLogger(__name__)

import  mana_conf
CONF = mana_conf.GetConf()


#INTERVAL = 200   
#THRESHOLD = 5

#API_HOST = '127.0.0.1'
#API_PORT = 8080
#GET_ALL_INSTANCE_URL = '/api/virs_list/'

#GET_METRIC = '/api/statics/'
#ALARM_OBJ = 'network_incoming_bytes_rate/'
#ALARM_TIME = '3h/'

#REGIONS = ['shanghai', 'beijing']

#unit_map = {"B/s":1,
#            "KB/s":1024, 
#            "MB/s":1024*1024,
#            "GB/s":1024*1024*1024
#       }

#RECEIVER = 'yangwanyuan@ztgame.com'
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

def run():
    interval = CONF.get('cycletime')
    #threshold = THRESHOLD
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
                #datas = get_network_flow(region, instance)
                #for data in datas:
                #    alarm(instance, data, threshold)
    except Exception, e:
        LOG.error(e)

def _monitor(region, instance):
    try:
        for (alarm_obj, thd) in CONF.get('alarm_list'):
            instance_id = instance.get('instance_id')
            datas = get_datas_from_api(region, instance_id, alarm_obj)
            #LOG.info("region:%s, instance:%s, alarm_obj:%s, datas:%s" %(region, instance, alarm_obj, datas))
            threshold = float(thd)
            for data in datas:
                alarm(instance, data, alarm_obj, threshold)
                #LOG.info(data)
                #alarm(instance, data, threshold)
    except Exception, e:
        LOG.error(e) 


def get_instances_from_api(region):
    url = CONF.get('url').get('get_all_instance_url') %region
    api_host = CONF.get('api_host')
    api_port = CONF.get('api_port')
    #url = GET_ALL_INSTANCE_URL + region + '/' 
    try:
        #con = httplib.HTTPConnection(API_HOST, API_PORT, timeout=30)
        #con.request('GET', url)
        #response = con.getresponse()
        #instances = simplejson.loads(response.read()).get('data')
        httpclient = HttpCon(api_host, api_port, url, "GET")
        body = httpclient.get()
        if body:
            instances = simplejson.loads(body).get('data')
    except Exception, e:
        LOG.error(e)
    return instances 

def get_datas_from_api(region, instance, alarm_obj):
    url = CONF.get('url').get('get_metric') %(region, alarm_obj, instance)
    api_host = CONF.get('api_host')
    api_port = CONF.get('api_port')
    #url = GET_METRIC + region + '/' + ALARM_OBJ + instance + '/' + ALARM_TIME
    try:
        httpclient = HttpCon(api_host, api_port, url, "POST")
        body = httpclient.get()
        if body:
            data = simplejson.loads(body)
    except Exception, e:
        LOG.error(e)
    #print("get instance %s's network is %s "%(instance,data) )
    return data


def alarm(instance, data, alarm_obj, threshold):
    try:
        bodys = data.get('data')
        device_name = data.get('name')
        instance_id =instance.get('instance_id')
        project = instance.get('project').encode('latin-1')
        user = instance.get('user').encode('latin-1')
        instance_name = instance.get('instance_name')
        if bodys == []:
            #print "%s's network %s:  NO data" %(instance, name)
            #LOG.info("%s's %s is %s:  NO data" %(instance, alarm_obj, name))
            return False
        #print data
        for body in bodys:
            unit = body.get('unit')
            multiple = unit_map.get(alarm_obj).get(unit)
            multiple = 1
            max_data = body.get('max')
            if max_data*multiple >  threshold:
                message =  " Instance_ID:%s\n Instance_Name:%s\n Project:%s\n User:%s\n AlarmBody:%s\n Device:%s\n Message:data is to high %s %s\n"\
                            %(instance_id, instance_name, project, user, alarm_obj, device_name, max_data, unit)
                #print message
                LOG.info(message)
                send_message(alarm_obj, message)
                return True
    except Exception, e:
        LOG.error(e)

def send_message(subject, message):
    try:
        email_host = CONF.get('email_host')
        email_port = CONF.get('email_port')
        sender = CONF.get('email_sender')
        sender_pwd = CONF.get('email_sender_pwd')
        receivers = CONF.get('email_receiver')
        emailclient = Email(email_host, email_port, sender, sender_pwd)
        for receiver  in receivers:
            msg = message
            subject = subject +  '   alarm!!!' 
            emailclient.sendmsg(receiver, subject, msg)
    except Exception,e:
        LOG.error(e)

    



if __name__ == "__main__":
    run()
