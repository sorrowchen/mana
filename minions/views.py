from django.shortcuts import render
from django.db import connections
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
import json
from api import ks_auth,c2_ssh
from api.beans import ComputeNodeMana
from api.public import NOVA_DB,NEUTRON_DB,NOVA,NEUTRON,RTN_200,RTN_500,getConnIp

import time

REGIONS=settings.REGIONS

"""
	LOG TYPE
        1.install minion
	2.update /etc/salt/minion  sed 
	3.service salt-minion restart
	4.master allow minion key [salt-key -y -a HOSTNAME ]
	5.master sync modules to minion 
"""

CMD_INIT_MINION="yum install -y salt-minion"
CMD_CONFIG_MINION="""sed -i "s/^#cachedir: \/var\/cache\/salt\/minion/cachedir: \/opt\/minion/1" /etc/salt/minion;mkdir /opt/minion;echo "%s salt">>/etc/hosts;service salt-minion restart"""
CMD_MASTER_SYNC="salt-key -y -a '{0}';sleep 3;salt '{1}' saltutil.sync_all"


CMD_MASTER_PASS="salt-key -y -a '%s'" 
CMD_SYNC_MASTER="salt '%s' saltutil.sync_all"


def init(req):
    ret=json.dumps(loop_compute_nodes())
    #if not ret=="[]":
	#ComputeNodeMana().addSaltLog(ret)
    return HttpResponse("%s" % ret)

def loop_compute_nodes():
    rets=[]
    for region in REGIONS:
	minions=ComputeNodeMana().getSaltComputeNodes(region)
	nodes=ComputeNodeMana().getAllComputeNodes(NOVA_DB(region))
	for node in nodes:
	    if minions.has_key("%s_%d"% (node.hypervisor_hostname,node.id)):
		#installed
		ret=updateOrNot(node,minions.get("%s_%d"% (node.hypervisor_hostname,node.id)),region)
		if ret:
		    rets.append(ret)
		    ComputeNodeMana().addSaltLog(ret,"UPDATE_NODE")
	    else:
		ret=install_new_minion(node,region)
		rets.append(ret)
    return rets

#INSTALLED,ING,ERROR
def updateOrNot(node,minion,region):
    if not node.running_vms == minion["running_vms"] or not node.deleted == minion["node_deleted"]:
	ComputeNodeMana().updateMinion(node.running_vms,node.deleted,minion["id"],region)
	return "update_minion(%s,%s):vms:%s->%s,node_deleted:%s->%s" % (node.hypervisor_hostname,node.host_ip,minion["running_vms"],node.running_vms,minion["node_deleted"],node.deleted)
    return None

def install_new_minion(node,region):
    #ADD MINION TO DB
    ComputeNodeMana().addMinion(node,region)
    salt_server=settings.C2_STATIC["Salt"]
    #REMOTE INSTALL MINION .
    state="INSTALLED"
    rets=[]
    try:
	LOG=c2_ssh.conn2(getConnIp(node.host_ip),CMD_INIT_MINION)
	rets.append("CMD_INIT_MINION:%s" % LOG)
	ComputeNodeMana().addSaltLog(LOG,"INSTALL_MINION")
	if "_error_" in LOG:
	    state="ERROR"
	else:
	    LOG=c2_ssh.conn2(getConnIp(node.host_ip),CMD_CONFIG_MINION % salt_server)
	    rets.append("CMD_CONFIG_MINION:%s" % LOG)
	    ComputeNodeMana().addSaltLog(LOG,"CONFIG_MINION")
    except Exception,ex:
	print Exception,":",ex
	LOG="SSH exception:%s" % str(ex)
	state="ERROR"
    time.sleep(3)

    if not "_error_" in LOG:
	rets.append(masterAcceptKey(node.hypervisor_hostname,rets))
	time.sleep(20)
	LOG=syncModules2Minion(node.hypervisor_hostname,rets)
	if "modules:" in LOG:
	    state="INSTALLED"
	rets.append(LOG)
    ComputeNodeMana().updateMinionState(state,node.id,region)
    return "install_new_minion:(%s,%s),state:%s,LOG:%s" % (node.hypervisor_hostname,node.host_ip,state,rets)

def masterSync(hostname):
    salt_server=settings.C2_STATIC["Salt"]
    print salt_server
    try:
	LOG=c2_ssh.conn2(salt_server,CMD_MASTER_SYNC.format(hostname,hostname))
	if "_error_" in LOG:
	    state="ERROR"
    except Exception,ex:
	print Exception,":",ex
	LOG="SSH exception:%s" % str(ex)
	state="ERROR"
    salt_log="Master accpect key and sync modules(host:%s):%s" % (hostname,LOG)
    ComputeNodeMana().addSaltLog(salt_log,"AcceptedKey_SYNC_MOD")
    return salt_log

def masterAcceptKey(hostname,rets):
    salt_server=settings.C2_STATIC["Salt"]
    try:
	LOG=c2_ssh.conn2(salt_server,CMD_MASTER_PASS % hostname)
	if "_error_" in LOG:
	    state="ERROR"
    except Exception,ex:
	print Exception,":",ex
	LOG="SSH exception:%s" % str(ex)
	state="ERROR"
    salt_log="Master accpect key(host:%s):%s" % (hostname,LOG)
    rets.append(salt_log)
    ComputeNodeMana().addSaltLog(salt_log,"Accepted_Key")

def syncModules2Minion(minionName,rets):
    salt_server=settings.C2_STATIC["Salt"]
    try:
	LOG=c2_ssh.conn2(salt_server,CMD_SYNC_MASTER % minionName)
	if "_error_" in LOG:
	    state="ERROR"
    except Exception,ex:
	print Exception,":",ex
	LOG="SSH exception:%s" % str(ex)
	state="ERROR"
    salt_log="Master sync all(host:%s):%s" % (minionName,LOG)
    rets.append(salt_log)
    ComputeNodeMana().addSaltLog(salt_log,"SYNC_ALL")

