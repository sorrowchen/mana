#!/usr/bin/python
#coding:utf-8

import Queue 

DATA_QUEUE = Queue.Queue()
ALARM_QUEUE = Queue.Queue()


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

class data_item:
    def __init__(self, instance = None, alarm_obj = None, threshold = None, region = None, data = None):
        self.instance = instance
        self.alarm_obj = alarm_obj
        self.threshold = threshold
        self.region = region
        self.data = data