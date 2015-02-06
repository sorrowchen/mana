from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings
from django.db import connections
from public import NOVA_DB,NEUTRON_DB,NOVA,NEUTRON,RTN_200,RTN_500,getConnIp
import ks_auth
import time
import utils
import base64,urllib,httplib,json,os
import urllib
from beans import InstanceManager,KeyStoneManager,NetworkFlowManager
import public

def index(req,uuid,region):
    token=ks_auth.getToken()
    UUID=uuid
    REGION=region
    return render_to_response('metric.html',locals())

def m1(req):
    token=ks_auth.getToken()
    expire=public.TOKEN["expire"]
    li=json.dumps(public.TOKEN)
    return render_to_response('m1.html',locals())

PERIOD={
    "3h":300,
    "1d":900,
    "7d":3600,
    "30d":21600,
}

DUR={
    "3h":3*3600,
    "1d":24*3600,
    "7d":7*24*3600,
    "30d":30*24*3600,
}

def connUrl(url):
	rtn=url.replace("http://","")
	return rtn[:(rtn.index("/"))] if "/" in rtn else rtn


def ifaceID(uuid,portid,instid):
    vir="instance-%s" % hex(instid)[2:].zfill(8)
    return "%s-%s-%s" % (vir,uuid,"tap"+portid[:11])

def multiLines():
    Meteric=Meteric.replace("_",".")

def statistics(region,Meteric,duration,RES_ID):
    metricUrl=KeyStoneManager().getServiceUrl("metering",region)
    token=ks_auth.getToken()
    print "token:",token
    headers1 = { "X-Auth-Token":token, "Content-type":"application/json" }
    now=int(time.time())
    duration_sec=DUR[duration]
    period_start=utils.msecs2utc(now-8*3600-duration_sec)
    data1={
        "Meteric":Meteric,
        "RES_ID":RES_ID,
        "period":PERIOD[duration],
        "period_start":urllib.quote(period_start,''),
    }
    print "metricUrl:",metricUrl
    print "->:",connUrl(metricUrl)
    conn1 = httplib.HTTPConnection(connUrl(metricUrl))
    m_url="/v2/meters/%(Meteric)s/statistics?q.field=resource_id&q.field=timestamp&q.op=eq&q.op=gt&q.type=&q.type=&q.value=%(RES_ID)s&q.value=%(period_start)s&period=%(period)s" % data1
    print "m_url:",m_url
    conn1.request("GET",m_url,None,headers1)
    response1 = conn1.getresponse()
    rtn = response1.read()
    conn1.close()
    if rtn:
	rtn = json.loads(rtn)
    print "rtn:",rtn
    return rtn


def statics(req,Meteric,UUID,duration,region):
    if not PERIOD.has_key(duration):
        return None
    vir=InstanceManager().getInstanceByID(NOVA_DB(region),UUID)
    if not vir:
        return None
    RTN=[]
    if "network" in Meteric:
        ports=NetworkFlowManager().getNetInfoByUUID(UUID,NEUTRON_DB(region))
        print ports
        for port in ports:
            obj={}
            obj["name"]=port["ip_address"]
            ifaceId=ifaceID(UUID,port["id"],int(vir.id))
            print "ifaceid:",ifaceId
            obj["data"]=statistics(region,Meteric.replace("_","."),duration,ifaceId)
            RTN.append(obj)
    elif "disk" in Meteric:
        obj={}
        obj["name"]=vir.hostname
        obj["data"]=statistics(region,Meteric.replace("_","."),duration,UUID)
        RTN.append(obj)
    elif "cpu_util"==Meteric:
        obj={}
        obj["name"]=vir.hostname
        obj["data"]=statistics(region,Meteric,duration,UUID)
        RTN.append(obj)
    return HttpResponse(json.dumps(RTN))



