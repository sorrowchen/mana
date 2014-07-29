from django.db import connections
from django.conf import settings
from django.http import HttpResponse
from beans import ComputeNodeMana,InstanceManager,KeyStoneManager,NetWorkManager,NetworkFlowManager,NetWorkFlow

from django.shortcuts import render_to_response
import json
import ks_auth
from public import NOVA_DB,NEUTRON_DB,NOVA,NEUTRON
import c2_ssh

DATABASES=settings.DATABASES
REGIONS=settings.REGIONS

nova_list=[region for region in DATABASES if(region.endswith("nova"))]
neutron_list=[region for region in DATABASES if(region.endswith("neutron"))]

def limitSu(req,region,uuid,network_flow,network_id):
    print "-- uuid:%s,su:%s,region:%s,network_id:%s --" % (uuid,network_flow,region,network_id)
    network_list=network_id.split("_")
    rtn={}
    for network in network_list:
	addSuc=NetWorkFlow().addNetWorkFlow(uuid,network_flow,region,network)
	if addSuc:
	    rtn=runScript(region,uuid,"INIT")
	else:
	    rtn={"add networkflow failed"}
    return HttpResponse("%s" % rtn)

def relimit(req,region,uuid,action):
    rtn=runScript(region,uuid,action)
    return HttpResponse("limitSu.%s" % rtn)

def runScript(region,uuid,action):
    #find host ip
    hostInfo=InstanceManager().getHostIp(NOVA_DB(region),uuid)
    if not hostInfo:
	return HttpResponse("Can't find host ip by uuid(%s) in Region(%s)" % (uuid,region))
    host_ip=hostInfo["host_ip"]
    su_list=NetWorkFlow().getNetWorkFlows(uuid,region)
    msg={}
    for su in su_list:
	 #find vir name by port
	port=NetworkFlowManager().getNetInfoByUUIDAndNetId(NEUTRON_DB(su["region"]),su["uuid"],su["network_id"])
	if not port:
	    continue
	virName="tap"+port["id"][0:11]
	netWorkName=port["network_name"]
	network_flow=su["network_flow"]
	script_params="start "+virName+" "+str(network_flow)+" "+str(network_flow)
	#command -------port_id network_flow start tapName 30 30
	script_name=settings.C2_LIMIT_NETWORK_FLOW_SCRIPT
	exe=script_name+" "+script_params
	print "runScript--->host_ip:%s,exe:%s" % (host_ip,exe)
	try:
	    LOG=c2_ssh.conn(host_ip,exe)
	except Exception,ex:
	    print Exception,":",ex
	    LOG="SSH exception:%s" % str(ex)
	msg[uuid+"_"+netWorkName]=LOG
	NetWorkFlow().addLog(uuid,region,su["network_id"],netWorkName,LOG,action)
    return msg
	
	
    
    





    



