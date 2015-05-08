from django.http import HttpResponse
from public import NOVA_DB,NEUTRON_DB,NOVA,NEUTRON,RTN_200,RTN_500,getConnIp
import ks_auth
import time
import utils
import base64,urllib,httplib,json,os
from beans import InstanceManager,KeyStoneManager,NetworkFlowManager,AlarmManager



def connUrl(url):
    rtn=url.replace("http://","")
    return rtn[:(rtn.index("/"))] if "/" in rtn else rtn

def ifaceID(uuid,portid,instid):
    vir="instance-%s" % hex(instid)[2:].zfill(8)
    return "%s-%s-%s" % (vir,uuid,"tap"+portid[:11])

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
        data.append(item)
    body = json.dumps({"code":200,"message":"ok","data":data},ensure_ascii=False, indent=2)
    return HttpResponse(body) 

####same wit statics, need fix later
def alarm_statics(req,Meteric,UUID,time,region):
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
            obj["data"]=alarm_statistics(region,Meteric.replace("_","."),time,ifaceId)
            RTN.append(obj)
    elif "disk" in Meteric:
        obj={}
        obj["name"]=vir.hostname
        obj["data"]=alarm_statistics(region,Meteric.replace("_","."),time,UUID)
        RTN.append(obj)
    elif "cpu_util"==Meteric:
        obj={}
        obj["name"]=vir.hostname
        obj["data"]=alarm_statistics(region,Meteric,time,UUID)
        RTN.append(obj)
    return HttpResponse(json.dumps(RTN))


def alarm_statistics(region,Meteric,duration,RES_ID):
    metricUrl=KeyStoneManager().getServiceUrl("metering",region)
    token=ks_auth.getToken()
    print "token:",token
    headers1 = { "X-Auth-Token":token, "Content-type":"application/json" }
    now=int(time.time())
    duration_sec=int(duration)
    period_start=utils.msecs2utc(now-8*3600-duration_sec)
    data1={
           "Meteric":Meteric,
           "RES_ID":RES_ID,
           "period":1,
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

def getAlarmTask(req, region, time):
    time = int(time)
    data=AlarmManager().getAlarmFromCycletime(region, time)
    #for line in data:
    #    instance_id = line.get('instance').get('instance_id')
    #    vir = InstanceManager().getInstanceByID(NOVA_DB(region),instance_id)
    #    line.get('instance')['user'] =  KeyStoneManager().getUserByUserID(vir.user_id)
    #    line.get('instance')['project'] = KeyStoneManager().getProjectByProjectID(vir.project_id)
    #    line.get('instance')['instance_name'] = vir.hostname 
    return HttpResponse(json.dumps({"code":200,"message":"ok","data":data},ensure_ascii=False, indent=2))
