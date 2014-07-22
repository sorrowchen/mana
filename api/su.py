from django.db import connections
from django.conf import settings
from django.http import HttpResponse
from beans import ComputeNodeMana,InstanceManager,KeyStoneManager,NetWorkManager,NetworkFlowManager

from django.shortcuts import render_to_response
import json
import ks_auth
from public import NOVA_DB,NEUTRON_DB,NOVA,NEUTRON
import c2_ssh

DATABASES=settings.DATABASES
REGIONS=settings.REGIONS

nova_list=[region for region in DATABASES if(region.endswith("nova"))]
neutron_list=[region for region in DATABASES if(region.endswith("neutron"))]

def limitSu(req,region,uuid,su):
    print "-region:%s,uuid:%s,su:%s--" % (region,uuid,su)
    addSuc=NetworkFlowManager().addNetworkFlow(uuid,su,region)
    if addSuc:
	pass
	#runScript()
    return HttpResponse("limitSu.")

def runScript():
    c2_ssh.conn(host,user,command)
    



