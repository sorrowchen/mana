#!/usr/bin/python
#coding=utf-8

import base64,urllib,httplib,json,os

from urlparse import urlparse
from django.conf import settings
import json
from beans import KeyStoneManager
import public
from public import NOVA_DB,NEUTRON_DB,NOVA,NEUTRON
import utils


def getTokenFromKS():
	headers1 = {"Content-type":"application/json" }
	KEYSTONE=settings.SYS_C2["KS_AUTH"]
	conn1 = httplib.HTTPConnection(connUrl(KEYSTONE))
	params1 = '{"auth": {"tenantName":"%(KS_TENANT)s", "passwordCredentials": {"username": "%(KS_USER)s", "password": "%(KS_PWD)s"}}}' % settings.SYS_C2
	conn1.request("POST","%s/tokens" % KEYSTONE ,params1,headers1)
	response1 = conn1.getresponse()
	data1 = response1.read()
	dd1 = json.loads(data1)
	apitoken = dd1['access']['token']['id']
	expire=dd1['access']['token']['expires']
	public.TOKEN["id"]=apitoken
	public.TOKEN["expire"]=utils.getNowAfterHours()
	conn1.close()
	return apitoken

def getToken():
    expire=public.TOKEN["expire"]
    print "expire:",expire
    now=utils.getlocalstrtime()
    print "now:",now
    if expire>now:
	print "expire>now"
        return public.TOKEN["id"]
    else:
	print "expire<now"
        return getTokenFromKS()


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
	rtn=url.replace("http://","")
	return rtn[:(rtn.index("/"))] if "/" in rtn else rtn

def getAvaZones(apitoken,region):
	Compute=KeyStoneManager().getServiceUrl("compute",region)
	print "getAvaZones compute ->%s" % Compute

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

def createNetwork(apitoken,region,segmentation_id,networkname,tenant_id):
	Network=KeyStoneManager().getServiceUrl("network",region,{"tenant_id":tenant_id})
	headers1 = { "X-Auth-Token":apitoken, "Content-type":"application/json" }
	conn1 = httplib.HTTPConnection(connUrl(Network))
	data={
		"network": {
        	"name": networkname,
        	"admin_state_up": True,
		"provider:segmentation_id":segmentation_id,
		"provider:network_type":"vlan",
		"provider:physical_network":"vlannet",
		"tenant_id":tenant_id,
		"shared":False
   	 	}
	}
	param=json.dumps(data)
	print param
	print "%s/networks" % Network
	conn1.request("POST","%s/v2.0/networks" % Network,param,headers1)
	response1 = conn1.getresponse()
	rtn = response1.read()
	conn1.close()
	if rtn:
	    rtn = json.loads(rtn)
	print rtn
	return rtn

def createSubnet(apitoken,region,cidr,network_id,tenant_id):
	Network=KeyStoneManager().getServiceUrl("network",region,{"tenant_id":tenant_id})
	headers1 = { "X-Auth-Token":apitoken, "Content-type":"application/json" }
	conn1 = httplib.HTTPConnection(connUrl(Network))
	data={
		"subnet": {
        	"network_id": network_id,
        	"cidr": cidr,
		"ip_version":4,
		"tenant_id":tenant_id,
		"enable_dhcp":True,
		"name":"%s-net" % cidr.split("/")[0],
		"gateway_ip":None
   	 	}
	}
	param=json.dumps(data)
	print param
	conn1.request("POST","%s/v2.0/subnets" % Network,param,headers1)
	response1 = conn1.getresponse()
	rtn = response1.read()
	conn1.close()
	#dd1 = json.loads(data1)
	if rtn:
	    rtn = json.loads(rtn)
	print rtn
	return rtn



