from django.db import connections
from django.conf import settings
from django.http import HttpResponse
from beans import ComputeNodeMana,InstanceManager,KeyStoneManager,NetWorkManager,EvaLog

from django.shortcuts import render_to_response
import json
import checker
import ks_auth
from public import NOVA_DB,NEUTRON_DB,NOVA,NEUTRON,RTN_200,RTN_500
import framework

DATABASES=settings.DATABASES
REGIONS=settings.REGIONS

nova_list=[region for region in DATABASES if(region.endswith("nova"))]
neutron_list=[region for region in DATABASES if(region.endswith("neutron"))]

def controller(req,ip,region=settings.REGIONS):
    if not checker.IsIpAddr(ip):
	rtn="check ip(%s) address failed" % ip
    else:
	ip_addr=req.META.get("REMOTE_ADDR",None)
	user=framework.getApiUserByToken(req)
	if not user:
	    return HttpResponse(RTN_500 % "Unknow auth token request." )
	regions=[]
	if not region ==settings.REGIONS:
	    regions.append(region)
	else:
	    regions=region
	rtn=eva(ip,regions)
	EvaLog().addLog(user,ip,rtn,ip_addr)
    return HttpResponse(rtn)

def eva(ip,regions):
    apitoken=ks_auth.getToken()
    if not apitoken:
	return RTN_500 % "Can't get token from keystone"

    for region in regions:
	if not NOVA(region) in nova_list:
		print "DB %s_nova doesn't configure." % region
		continue
	if not NEUTRON(region) in neutron_list:
		print "DB %s_neutron doesn't configure." % region
		continue
	print "---------Start to query instanceId from db(%s)-------------" % region
	instanceBean=InstanceManager().findInstanceIdByIp(NEUTRON_DB(region),NOVA_DB(region),ip)
	if not instanceBean:
		print "can't find instance in db(%s) by vir" % region
		print "------- check if it's a physical machine --------"		
		childs=InstanceManager().getChildrens(NOVA_DB(region),ip)
		
		print childs
		
		if not childs:
		    if isinstance(childs,list):
			return RTN_500 % ("[] instance find in nova.instances by physical machine(%s) in Region(%s)" % (ip,region))
	       	    print "can't find it as a physical machine in db(%s)" % region
		    continue
		msg={}
		for child in childs:
			msg["uuid_%s" % child.uuid]=evacuate(apitoken,child,region,child.host)
		return RTN_200 % msg
	else:
		mess=evacuate(apitoken,instanceBean,region,instanceBean.host)
		return RTN_200 % mess
    return RTN_500 % ("Can't find machine|virtual by ip (%s)" % ip)	


from su import runScript

def evacuate(apitoken,instanceBean,region,filterHost=None):
	node=getFilterAvailabilityHost(region,instanceBean.vcpus,instanceBean.memory_mb,filterHost,apitoken)
	if not node:
	    node=getAvailabilityHost(region,instanceBean.vcpus,instanceBean.memory_mb,filterHost,apitoken)
	else:
	    print "find filter node %s" % node
	if not node:
	    return "no compute node match"
	else:
	    rtn=ks_auth.evacuate(apitoken,region,instanceBean.uuid,node.hypervisor_hostname)	
	    print "%s <br/> adapt by<br/>  %s <br/> %s" % (instanceBean,node,rtn)
	    if rtn.has_key("evacuate"):
	    	runScript(region,instanceBean.uuid,"EVACUATE")	
	    return rtn

def getFreeResByRegion(req,region=None):
    if not region or not region in nova_list:
	return HttpResponse("region(%s) doesn't exist." % region)
    nodes=ComputeNodeMana().getComputeNodes(NOVA_DB(region))
    #return HttpResponse(json.dumps(nodes), content_type="application/json")
    return HttpResponse(nodes)

def getAvailabilityHost(region,cpu,mem,filterHost=None,apitoken=None):
    print "cpu %s mem %s" % (cpu,mem)	
    
    nodes=ComputeNodeMana().getComputeNodes(NOVA_DB(region))
    print "nodes %s " % nodes

    service=ks_auth.getOsServices(apitoken,region)
    if not service:
	return HttpResponse("Can't get service status.")

    for node in nodes:
	if filterHost and filterHost==node.hypervisor_hostname:
		continue
	if not service.has_key(node.hypervisor_hostname) or service[node.hypervisor_hostname]=="down":
		continue
	if node.availability(cpu,mem):
	    return node
    return None

def getFilterAvailabilityHost(region,cpu,mem,filterHost=None,apitoken=None):

    zones=ks_auth.getAvaZones(apitoken,region)
    
    if not zones.has_key(settings.BACK_UP_AZ) or not zones[settings.BACK_UP_AZ]:
	print "Can't find backupAZ compute nodes"
	return None

    backupAZ=zones[settings.BACK_UP_AZ]

    #filters=",".join(backupAZ)

    nodes=ComputeNodeMana().getFilterComputeNodes(NOVA_DB(region),backupAZ)

    for node in nodes:
	if node.availability(cpu,mem):
	    return node
    return None

def test(req):
    addr=req.META.get("REMOTE_ADDR",None)
    return HttpResponse("%s" % addr)

def getMachineInfoByIp(req,ip):
    apitoken=ks_auth.getToken()
    if not apitoken:
	return HttpResponse("Can't get token from keystone")

    for region in REGIONS:
	if not NOVA(region) in nova_list:
		print "DB %s_nova doesn't configure." % region
		continue
	if not NEUTRON(region) in neutron_list:
		print "DB %s_neutron doesn't configure." % region
		continue
	print "---------Start to query instanceId from db(%s)-------------" % region
	instanceBean=InstanceManager().findInstanceIdByIp(connections[NEUTRON(region)],connections[NOVA(region)],ip)
	if not instanceBean:
		print "can't find instance in db(%s) by vir" % region
		print "------- check if it's a physical machine --------"		
		cnode=ComputeNodeMana().getComputeNodeByIp(ip,connections[NOVA(region)])
		
		if cnode:
		    return HttpResponse("Region(%s),physical machine info:%s" % (region,cnode))
	else:
		return HttpResponse("Region(%s),virtual instance info:%s" % (region,instanceBean))
    return HttpResponse("Can't get machine info.")

def getServiceStatus(req):
    apitoken=ks_auth.getToken()
    if not apitoken:
	return HttpResponse("Can't get token from keystone")
    response=""
    for region in REGIONS:
        service=ks_auth.getOsServices(apitoken,region)
        if not service:
	    return HttpResponse("Can't get service status from Region %s" % region)
        else:
	    response+="<hr><span style='color:blue'>Region:%s</span><br/>" % region
	    for k,v in service.items():
		if v=="down":
		    response+=k+"&nbsp&nbsp<span style='color:red'>"+v+"</span><br/>"
		else:
		    response+=k+"&nbsp&nbsp"+v+"<br/>"

    return HttpResponse(response)	
	
def az_list(req):
    apitoken=ks_auth.getToken()
    if not apitoken:
	return HttpResponse("Can't get token from keystone")
    zones=ks_auth.getAvaZones(apitoken,"RegionOne")
    if not zones:
	return HttpResponse("Can't get az - compute nodes.")
    else:
	json_str=json.dumps(zones)
	return render_to_response('json.html',locals())

def getFreeRes(req):
    regions={}
    for nova_db in nova_list:
	nodes=ComputeNodeMana().getComputeNodes(connections[nova_db])
	regions[nova_db]=nodes
	print nodes
    #nodes=ComputeNodeMana().getComputeNodes(connections["dev112_nova"])
    return render_to_response('free_res.html',locals())

def ip_list(req):
    regions={}
    totals={}
    print  neutron_list
    for neutron_db in neutron_list:
	ips=NetWorkManager().getFreeIp(connections[neutron_db])
	print "ips %s" % ips
	regions[neutron_db]=ips
	totals[neutron_db]=json.dumps(NetWorkManager().getAllTotalNum(ips,connections[neutron_db]))
    print regions
    print totals
    return render_to_response('ip_list.html',locals())

def ip_list_region(req,region):
    if not region in REGIONS:
	return HttpResponse("""{"code":500,"message":"region doesn't exist"}""")		
    neutron_db=NEUTRON_DB(region)
    ips=NetWorkManager().getFreeIp(neutron_db)
    obj=json.dumps(NetWorkManager().getAllTotalNum(ips,neutron_db))
    return HttpResponse(obj)

def get_ava_network(req,region,nets):
    if not region in REGIONS:
	return HttpResponse("""{"code":500,"message":"region doesn't exist"}""")		
    neutron_db=NEUTRON_DB(region)
    ips=NetWorkManager().getFreeIp(neutron_db)
    nodes=NetWorkManager().getAllTotalNum(ips,neutron_db)
    array=nets.split("_")
    obj=[]
    for tag in array:
	check=getAvaNetworkId(nodes,tag)
	if check==0:
	    return HttpResponse("""{"code":500,"message":"no free ip in %s."}""" % tag)
	obj.append(check)
    return HttpResponse("""{"code":200,"message":"ok","data":"%s"}""" % ",".join(obj)) 

def getAvaNetworkId(nodes,tag):
    for k,v in nodes.items():
	if tag in k and v["freeNum"]>0:
	    return v["network_id"]
    return 0

def virs_list(req,region):
    REGION=region
    virs=InstanceManager().getallActiveInstances(NOVA_DB(region))
    data = []
    for vir in virs:
        item= {}
        item['instance_id']= vir.uuid
        item['user'] = KeyStoneManager().getUserByUserID(vir.user_id)
        item['project'] = KeyStoneManager().getProjectByProjectID(vir.project_id)
        item['instance_name'] = vir.hostname
        #data.append(vir.uuid)
        data.append(item)
    body = json.dumps({"code":200,"message":"ok","data":data})
    return HttpResponse(body) 





