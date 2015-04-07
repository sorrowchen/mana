#!/usr/bin/pyhon

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


INTERVAL = 200   
THRESHOLD = 5

API_HOST = '127.0.0.1'
API_PORT = 8080
GET_ALL_INSTANCE_URL = '/api/virs_list/'

GET_METRIC = '/api/statics/'
ALARM_OBJ = 'network_incoming_bytes_rate/'
ALARM_TIME = '3h/'

REGIONS = ['shanghai', 'beijing']

unit_map = {"B/s":1,
            "KB/s":1024, 
            "MB/s":1024*1024,
            "GB/s":1024*1024*1024
       }

RECEIVER = 'yangwanyuan@ztgame.com'

def run():
    interval = INTERVAL
    threshold = THRESHOLD
    LOG.info("begin to monitor,every %s seconds" %interval)
    while True:
        try:
            time_pre = time.time()
            monitor(threshold)
            time_now = time.time()
            time.sleep(interval + time_pre - time_now)
        except Exception, e:
            LOG.error(e)
	

def monitor(threshold):
    for region in REGIONS:
        instances = get_all_instance(region)
        for instance in instances:
            datas = get_network_flow(region, instance)
            for data in datas:
                alarm(instance, data, threshold)

def get_all_instance(region):
    url = GET_ALL_INSTANCE_URL + region + '/' 
    try:
        #con = httplib.HTTPConnection(API_HOST, API_PORT, timeout=30)
        #con.request('GET', url)
        #response = con.getresponse()
        #instances = simplejson.loads(response.read()).get('data')
        httpclient = HttpCon(API_HOST, API_PORT, url, "GET")
        body = httpclient.get()
        if body:
            instances = simplejson.loads(body).get('data')
    except Exception, e:
        LOG.error(e)
    return instances 

def get_network_flow(region, instance):
    url = GET_METRIC + region + '/' + ALARM_OBJ + instance + '/' + ALARM_TIME
    try:
        httpclient = HttpCon(API_HOST, API_PORT, url, "POST")
        body = httpclient.get()
        if body:
            data = simplejson.loads(body)
    except Exception, e:
        LOG.error(e)
    #print("get instance %s's network is %s "%(instance,data) )
    return data


def alarm(instance, data, threshold):
    bodys = data.get('data')
    name = data.get('name')
    if bodys == []:
        #print "%s's network %s:  NO data" %(instance, name)
        LOG.info("%s's network %s:  NO data" %(instance, name))
        return False
    #print data
    for body in bodys:
        unit = body.get('unit')
        multiple = unit_map.get(unit)
        max_data = body.get('max')
        if max_data*multiple >  threshold:
            message =  "%s's network %s:   data is to high %s %s"%(instance, name, max_data, unit)
            #print message
            LOG.info(message)
            send_message(instance,  message)
            return True

def send_message(instance,  message):
    emailclient = Email()
    msg = message
    subject = 'network alarm!!!'
    receiver = RECEIVER
    emailclient.sendmsg(receiver, subject, msg)

    



if __name__ == "__main__":
    run()
