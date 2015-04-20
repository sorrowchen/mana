#!/usr/bin/python
#coding:utf-8


import mana_log
LOG = mana_log.GetLog(__name__)

import  mana_conf
CONF = mana_conf.GetConf()

from mana_public import DATA_QUEUE,ALARM_QUEUE
from mana_public import data_item, msg_item


def monitor():
    LOG.info("Begin to monitor thread")
    while True:
        if not DATA_QUEUE.empty():
            item= DATA_QUEUE.get()
            _monitor(item)


def _monitor(data_item):
    datas = data_item.data
    for data in datas:
        check_data(data_item.instance, data, data_item.alarm_obj, data_item.threshold, data_item.region)

def check_data(instance, data, alarm_obj, threshold, region):
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
                    max_data = round((max_data * 8 / (1024 * 1024)), 2)  
                    unit = 'Mbits'
                msg_body = msg_item(alarm_obj, instance_id, instance_name, project, user, device_name, max_data, unit, region)
                ALARM_QUEUE.put(msg_body)
                return True
    except Exception, e:
        LOG.error(e)



if __name__ == "__main__":
    monitor()