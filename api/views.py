from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password


import datetime

from django.conf import settings
from django.db import connections

import passlib
import passlib.hash
from public import NOVA_DB,NEUTRON_DB,NOVA,NEUTRON,RTN_200,RTN_500,getConnIp
import framework
from beans import C2Keystone,InstanceManager

REGIONS=settings.REGIONS

def index(req):
    regions=REGIONS
    return render_to_response('index.html',locals())

def chgPwd(req,userid,pwd):
    ip_addr=req.META.get("REMOTE_ADDR",None)
    user=framework.getApiUserByToken(req)
    #user="test"
    if not user:
        return HttpResponse(RTN_500 % "Unknow auth token request." )
    print "chgPwd(ip:%s)---%s update password=%s where userid=%s" % (ip_addr,user,pwd,userid)
    password=passlib.hash.sha512_crypt.encrypt(pwd,rounds=40000)
    C2Keystone().chgPwd(userid,password)
    return HttpResponse(RTN_200 % "update password success")

def evacuate(req,host='uuid'):
    return render_to_response('eva.html',locals())

import json

def face(req):
    data={"answer":"answer"}
    return HttpResponse(json.dumps(data))   


def eva(req):
    if req.method=='POST':
        ip=req.POST.get("ip")
        return HttpResponse("post ip %s" % ip)
    else:
        ip=req.GET.get("ok","default value")
        addr="addr"
        return HttpResponse("get ip %s,%s" % (ip,addr))

def virs(req,region):
    REGION=region
    virs=InstanceManager().getallActiveInstances(NOVA_DB(region))
    pre=""
    RTN={}
    for vir in virs:
        key=vir.host
        if pre=="" or not pre==key:
            RTN[""+key]=[]
        RTN[key].append(vir)
        pre=key
    return render_to_response('virs.html',locals())


