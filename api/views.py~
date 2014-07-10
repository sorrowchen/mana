from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password


import datetime

from django.conf import settings
from django.db import connections

def index(req):
    return render_to_response('index.html',locals())


def evacuate(req,host='uuid'):
    current_date=datetime.datetime.now()    
    db=settings.DATABASES
    pwd=make_password("huming")
    mana1=connections['mana']
    cursor=mana1.cursor()
    cursor.execute("select count(*) from instances")
    result=cursor.fetchone()
    # connections['mana'].commit()
    cursor.close()
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

	  
