from django.db import connections
from django.conf import settings
from django.http import HttpResponse
from beans import ComputeNodeMana,InstanceManager,KeyStoneManager,NetWorkManager,NetworkFlowManager,NetWorkFlow,C2cidrManager

from django.shortcuts import render_to_response
import json
import ks_auth
from public import NOVA_DB,NEUTRON_DB,NOVA,NEUTRON,RTN_200,RTN_500
import c2_ssh
import base64
import framework

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
	    rtn=RTN_200 % runScript(region,uuid,"INIT")
	else:
	    rtn=RTN_500 % "add networkflow failed"
    return HttpResponse(rtn)

def relimit(req,region,uuid,action):
    if action not in ["RESTART","EVACUATE","INIT"]:
	return  HttpResponse(RTN_500 % "Unknow limit su action request.")
    rtn=runScript(region,uuid,action)
    return HttpResponse(rtn)

def chgPwd(req,uuid,region,pwd):
    user=framework.getApiUserByToken(req)
    #if not user:
	#return HttpResponse(RTN_500 % "Unknow auth token request.")
    hostInfo=InstanceManager().getHostIp(NOVA_DB(region),uuid)
    if not hostInfo:
	return HttpResponse(RTN_500 % ("Can't find host ip by uuid(%s) in Region(%s)" % (uuid,region)))
    host_ip=hostInfo["host_ip"]
    instid=int(hostInfo["id"])
    vir="instance-%s" % hex(instid)[2:].zfill(8)
    script_name=settings.C2_CHANGE_VIR_PWD_SCRIPT
    exe="%s %s %s" %(script_name,vir,pwd)
    print "runScript--->host_ip:%s,exe:%s" % (host_ip,exe)
    try:
	LOG=c2_ssh.conn(host_ip,exe)
    except Exception,ex:
	print Exception,":",ex
	LOG="SSH exception:%s" % str(ex)
    return HttpResponse((RTN_200 % LOG) if "True" in LOG else (RTN_500 % LOG))

def runScript(region,uuid,action):
    #find host ip
    hostInfo=InstanceManager().getHostIp(NOVA_DB(region),uuid)
    if not hostInfo:
	return HttpResponse(RTN_500 % "Can't find host ip by uuid(%s) in Region(%s)" % (uuid,region))
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
    return RTN_200 % msg
	

def getUserNetwork(req,region,tenant_id,networkname):
    obj=C2cidrManager().getFreecidr(tenant_id,region)
    if not obj:
	return HttpResponse("""{"code":500,"messaage":"Can't find cidr."}""") 
    if not obj["network_id"]:
	apitoken=ks_auth.getToken()
	if not apitoken:
	    return HttpResponse("""{"code":500,"messaage":"Can't get token from keystone"}""")
	#create network
	data=ks_auth.createNetwork(apitoken,region,obj["id"],base64.standard_b64decode(networkname),tenant_id)
	if not data or data.has_key("NeutronError"):
	    return HttpResponse("""{"code":500,"messaage":"Can't get data from create-network api.","data":"%s"}""" % (None if not data else data)) 
	network=data["network"]["id"]
	#create subnet	
	data2=ks_auth.createSubnet(apitoken,region,obj["cidr"],network,tenant_id)
	if not data2 or data2.has_key("NeutronError"):
	    return HttpResponse("""{"code":500,"messaage":"Can't get data from create-subnet api.","data":"%s"}""" % (None if not data2 else data2)) 
	#update cidr
	C2cidrManager().useCidr(int(obj["id"]),tenant_id,network,region)
	return HttpResponse("""{"code":200,"messaage":"ok","data":"%s"}""" % network)
    else:
	return HttpResponse("""{"code":200,"messaage":"ok","data":"%s"}""" % obj["network_id"])

    
    





    



