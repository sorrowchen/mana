#!/usr/bin/python
#coding=utf-8

import base64,urllib,httplib,json,os

from urlparse import urlparse
from django.conf import settings
import json
from beans import KeyStoneManager
from public import NOVA_DB,NEUTRON_DB,NOVA,NEUTRON

def getToken():
	#headers1 = { "X-Auth-Token":"422172848609489ea8126be290b4687f", "Content-type":"application/json" }
	headers1 = {"Content-type":"application/json" }

	KEYSTONE=settings.SYS_C2["KS_AUTH"]
	conn1 = httplib.HTTPConnection(connUrl(KEYSTONE))

	params1 = '{"auth": {"tenantName":"%(KS_TENANT)s", "passwordCredentials": {"username": "%(KS_USER)s", "password": "%(KS_PWD)s"}}}' % settings.SYS_C2

	conn1.request("POST","%s/tokens" % KEYSTONE ,params1,headers1)

	response1 = conn1.getresponse()

	data1 = response1.read()

	dd1 = json.loads(data1)

	apitoken = dd1['access']['token']['id']
	
	print apitoken

	conn1.close()
	return apitoken

def evacuate(apitoken,region,server_id,targetHost):
	
	Compute=KeyStoneManager().getServiceUrl("compute",region)

	headers1 = { "X-Auth-Token":apitoken, "Content-type":"application/json" }
	conn1 = httplib.HTTPConnection(connUrl(Compute))
	
	param=json.dumps({"evacuate": {"host":targetHost,"onSharedStorage": "False"}})
	print param
	
	conn1.request("POST","%s/servers/%s/action" % (Compute,server_id),param,headers1)

	response1 = conn1.getresponse()

	rtn = response1.read()
	conn1.close()
	#dd1 = json.loads(data1)
	if rtn:
	    rtn = json.loads(rtn)

	print rtn
	return rtn

def getOsServices(apitoken,region):
	Compute=KeyStoneManager().getServiceUrl("compute",region)

	headers1 = { "X-Auth-Token":apitoken, "Content-type":"application/json" }

	conn1 = httplib.HTTPConnection(connUrl(Compute))

	conn1.request("GET","%s/os-services" % Compute,None,headers1)

	response1 = conn1.getresponse()

	rtn = response1.read()

	conn1.close()

	print "getOsServices:os-services->%s" % response1

	#dd1 = json.loads(data1)
	if not rtn:
		return None


	
	rtn = json.loads(rtn)
	services={}

	for service in rtn['services']:
	    if not service["binary"]=="nova-compute" or service["zone"]=="internal":
		continue
	    services[service["host"]]=service["state"]
	
	print "----------------------------------------------------"
	print services
	return services

def connUrl(url):
	print url
	rtn=url.replace("http://","")
	lastIndex=rtn.index("/")
	return rtn[0:lastIndex]

def getAvaZones(apitoken,region):
	print "region %s" % region
	Compute=KeyStoneManager().getServiceUrl("compute",region)
	print Compute

	headers1 = { "X-Auth-Token":apitoken, "Content-type":"application/json" }

	conn1 = httplib.HTTPConnection(connUrl(Compute))

	conn1.request("GET","%s/os-availability-zone/detail" % Compute,None,headers1)

	response1 = conn1.getresponse()

	rtn = response1.read()
	conn1.close()

	if not rtn:
		return None
	
	rtn = json.loads(rtn)
	zones={}

	print rtn

	for zone in rtn['availabilityZoneInfo']:
	    if zone["zoneName"]=="internal" or not zone["zoneState"]["available"]:
		continue
	    zones[zone["zoneName"]]=[]
	    for k,v in zone["hosts"].items():
		if not v["nova-compute"]["available"] or not v["nova-compute"]["active"]:
		    continue
		zones[zone["zoneName"]].append(k)
	
	print "----------------------------------------------------"
	print zones
	return zones


"""
apitoken = dd1['access']['token']['id']

apitenant= dd1['access']['token']['tenant']['id']

apiurl = dd1['access']['serviceCatalog'][0]['endpoints'][0]['publicURL']
18
apiurlt = urlparse(dd1['access']['serviceCatalog'][0]['endpoints'][0]['publicURL'])
19
 
20
url2 = apiurlt[1]
21
params2 = urllib.urlencode({})
22
headers2 = { "X-Auth-Token":apitoken, "Content-type":"application/json" }
23
conn2 = httplib.HTTPConnection(url2)
24
conn2.request("GET", "%s/servers" % apiurlt[2], params2, headers2)
25
response2 = conn2.getresponse()
26
data2 = response2.read()
27
dd2 = json.loads(data2)
28
conn2.close()
29
for i in range(len(dd2['servers'])):
30
    print dd2['servers'][i]['name']
"""
