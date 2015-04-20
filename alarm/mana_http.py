#!/usr/bin/python
#coding:utf-8

import httplib
import urllib2

#the httpclient use for RESTful API
class HttpCon():
    def __init__(self, host = None, port = None, url = None, method = None, timeout = 30):
        self.host = host
        self.port = port
        self.url = url
        self.method = method
        self.timeout = 30

    def get(self):
        try:
            self.con = httplib.HTTPConnection(self.host, self.port, self.timeout)
            self.con.request(self.method, self.url)
            response = self.con.getresponse()
            status = response.status 
            if status != 200:
                return None
            return response.read()
        except Exception, e:
            print e

    def __del__(self):
        if self.con:
            self.con.close()

#the urlclient use for url 
class UrlCon():
    def __init__(self, host = None, port = None, url = None, method = None, timeout = 30):
        self.host = host
        self.port = port
        self.url = url
        self.method = method
        self.timeout = 30

    def get(self):
        try:
            full_url = 'http://' + self.host +':' + str(self.port) + self.url
            response = urllib2.urlopen(full_url)
            result = response.read()
            return result
        except Exception, e:
            print e

    def __del__(self):
        pass

    
   
if __name__ == "__main__":
    #httpclient = HttpCon("www.baidu.com", 80, "/", "GET")
    #print httpclient.get()
    
    urlclient = UrlCon("192.168.39.120", 29997, "/emaysendMsg?dest_mobile=18505532175&msg_content=%B6%CC%D0%C5%B2%E2%CA%D4%A1%BE%BE%DE%C8%CB%CD%F8%C2%E7%A1%BF&priority=5&gametype=2&acttype=89", "GET")
    print urlclient.get()
