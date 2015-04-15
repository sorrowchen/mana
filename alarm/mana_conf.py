#!/usr/bin/python
#coding:utf-8

import ConfigParser
import os



def Parser(config):
    try:
        conf = {}
        conf['cycletime'] = config.getint('global', 'cycletime')
        conf['api_host'] = config.get('global', 'api_host')
        conf['api_port'] = config.getint('global', 'api_port')

        regions_list = config.get('global', 'regions').split(',')
        conf['regions'] = regions_list

        url_dict = {}
        url_dict['get_all_instance_url'] = config.get('url', 'get_all_instance_url')
        url_dict['get_metric'] = config.get('url', 'get_metric')
        conf['url'] = url_dict


        conf['email_host'] = config.get('email', 'email_host')
        conf['email_port'] = config.getint('email', 'email_port')
        conf['email_sender'] = config.get('email', 'email_sender')
        conf['email_sender_pwd'] = config.get('email', 'email_sender_pwd')

        email_receiver_list = config.get('email', 'email_receiver').split(',')
        conf['email_receiver'] = email_receiver_list

        alarm_list = config.items('alarm')
        conf['alarm_list'] = alarm_list

        conf['phone_host'] = config.get('phone', 'phone_host')
        conf['phone_port'] = config.getint('phone', 'phone_port')
        conf['phone_gametype'] = config.get('phone', 'phone_gametype')
        conf['phone_priority'] = config.get('phone', 'phone_priority')
        conf['phone_acttype'] = config.get('phone', 'phone_acttype')

        phone_receiver_list = config.get('phone', 'phone_receiver').split(',')
        conf['phone_receiver'] = phone_receiver_list

    except Exception, e:
        print e

    return conf

def GetConf():
    try:
        config = ConfigParser.ConfigParser()
        config.read('/etc/mana/mana_monitor.conf')
        conf = Parser(config) 
    except Exception, e:
        print e
    return conf




if __name__ == '__main__':
    con = GetConf()
    print con



