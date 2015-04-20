#!/usr/bin/python
#coding:utf-8

import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

import threading
import time

from mana_collection import collection
from mana_monitor import monitor
from mana_alarm import alarm

def start():
    DataCollection = threading.Thread(target = collection, name = "DataCollection")
    Monitor = threading.Thread(target = monitor, name = "Monitor")
    Alarm = threading.Thread(target = alarm,  name = "Alarm") 

    DataCollection.setDaemon(True)
    Monitor.setDaemon(True)
    Alarm.setDaemon(True)
    
    DataCollection.start()
    Monitor.start()
    Alarm.start()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    start()