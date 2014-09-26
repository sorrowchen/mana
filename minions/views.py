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

REGIONS=settings.C2_STATIC["Regions"]

"""
	LOG TYPE
        1.install minion
	2.update /etc/salt/minion  sed 
		sed -i "s/^#cachedir: \/var\/cache\/salt\/minion/cachedir: \/opt\/minion/1" /etc/salt/minion
		sed -i "s/^#master: salt/master: 172\.30\.250\.22/1" /etc/salt/minion
		sed -i "s/^#open_mode: False/open_mode: True/1" /etc/salt/minion
	3.service salt-minion restart
	4.master allow minion key [salt-key -y -a HOSTNAME ]
	5.master sync modules to minion 
"""

CMD_INIT_MINION="yum remove -y salt-minion;yum install -y salt-minion"
CMD_CONFIG_MINION="""sed -i "s/^#master: salt/master: %s/1" /etc/salt/minion;service salt-minion start"""

CMD_MASTER_SYNC="salt-key -y -a '{0}';sleep 3;salt '{1}' saltutil.sync_all"

CMD_MASTER_PASS="salt-key -y -a '%s'" 
CMD_SYNC_MASTER="salt '%s' saltutil.sync_all"

def init(req):
    ret=json.dumps(loop_compute_nodes())
    #if not ret=="[]":
	#ComputeNodeMana().addSaltLog(ret)
    return HttpResponse("%s" % ret)

def loop_compute_nodes():
    print "run loop_compute_nodes"
    print REGIONS
    rets=[]
    for region in REGIONS:
	minions=ComputeNodeMana().getSaltComputeNodes(region)
	nodes=ComputeNodeMana().getAllComputeNodes(NOVA_DB(region))
	print "region:%s,minions:%s,nodes:%s" % (region,len(minions),len(nodes))
	for node in nodes:
	    print "run check node:%s" % node
	    if minions.has_key("%s_%d"% (node.hypervisor_hostname,node.id)):
		#installed
		ret=updateOrNot(node,minions.get("%s_%d"% (node.hypervisor_hostname,node.id)),region)
		if ret:
		    rets.append(ret)
		    ComputeNodeMana().addSaltLog(ret,"UPDATE_NODE")
	    else:
		print "start to install new minion--- %s" % node
		ret=install_new_minion(node,region)
		rets.append(ret)
    print "end run loop_compute_nodes"
    return rets

#INSTALLED,ING,ERROR
def updateOrNot(node,minion,region):
    if not node.running_vms == minion["running_vms"] or not node.deleted == minion["node_deleted"]:
	ComputeNodeMana().updateMinion(node.running_vms,node.deleted,minion["id"],region)
	return "update_minion(%s,%s):vms:%s->%s,node_deleted:%s->%s" % (node.hypervisor_hostname,node.host_ip,minion["running_vms"],node.running_vms,minion["node_deleted"],node.deleted)
    return None

def install_new_minion(node,region):
    print "ADD MINION TO DB"
    ComputeNodeMana().addMinion(node,region)
    salt_master=settings.C2_STATIC["Salt_master"]
    state="INSTALLED"
    rets=[]
    print "------------start to install minion ------------------"
    try:
	LOG=c2_ssh.conn2(getConnIp(node.host_ip),CMD_INIT_MINION)
	rets.append("CMD_INIT_MINION:%s" % LOG)
	print "install log:%s" % LOG
	ComputeNodeMana().addSaltLog("INSTALL_MINION:%s" % LOG,"INSTALL_MINION")
    except Exception,ex:
	LOG="install_new_minion exception:%s" % str(ex)
	ComputeNodeMana().addSaltLog("(%s)_INSTALL_ERROR:%s" % (node.hypervisor_hostname,LOG),"INSTALL_ERROR")
	print LOG
	print Exception,"install_new_minion:",ex
	state="ERROR"
    print "----------------finish install minion --------------------------"
    print "----------------start to update minion config-------------------"
    try:
	LOG=c2_ssh.conn2(getConnIp(node.host_ip),CMD_CONFIG_MINION % salt_master)
	rets.append("CMD_CONFIG_MINION:%s" % LOG)
	print "update config log:%s" % LOG
	ComputeNodeMana().addSaltLog("CONFIG_ERROR:%s" % LOG,"CONFIG_MINION")
    except Exception,ex:
	LOG="CONFIG_MINION exception:%s" % str(ex)
	ComputeNodeMana().addSaltLog("(%s)_CONFIG_MINION_ERROR:%s" % (node.hypervisor_hostname,LOG),"CONFIG_ERROR")
	print LOG
	print Exception,"CMD_CONFIG_MINION:",ex
	state="ERROR"
    print "----------------finish update minion config------------------------"
    if "_error_" in LOG:
	print LOG
        ComputeNodeMana().updateMinionState("INIT_ERROR",node.id,region)

    time.sleep(60)
    if not "_error_" in LOG:
	rets.append(masterAcceptKey(node.hypervisor_hostname,node.id,region))
	time.sleep(60)
#	LOG=syncModules2Minion(node.hypervisor_hostname,node.id,region)
	if "modules:" in LOG:
	    state="INSTALLED"
	    ComputeNodeMana().updateMinionState(state,node.id,region)
	rets.append(LOG)

    return "install_new_minion:(%s,%s),state:%s,LOG:%s" % (node.hypervisor_hostname,node.host_ip,state,rets)

def masterSync(hostname):
    salt_server=settings.C2_STATIC["Salt"]
    print salt_server
    try:
	LOG=c2_ssh.conn2(salt_server,CMD_MASTER_SYNC.format(hostname,hostname))
	if "_error_" in LOG:
	    state="ERROR"
    except Exception,ex:
	print Exception,"masterSync:",ex
	LOG="masterSync exception:%s" % str(ex)
	state="SYNC_ERROR"
    salt_log="Master accpect key and sync modules(host:%s):%s" % (hostname,LOG)
    ComputeNodeMana().addSaltLog(salt_log,"AcceptedKey_SYNC_MOD")
    return salt_log

def masterAcceptKey(hostname,node_id,region):
    salt_server=settings.C2_STATIC["Salt"]
    try:
	LOG=c2_ssh.conn2(salt_server,CMD_MASTER_PASS % hostname)
	if "_error_" in LOG:
	    state="ERROR"
    except Exception,ex:
	print Exception,"masterAcceptKey:",ex
	LOG="masterAcceptKey exception:%s" % str(ex)
	ComputeNodeMana().updateMinionState("KEY_ERROR",node_id,region)
    salt_log="Master accpect key(host:%s):%s" % (hostname,LOG)
    ComputeNodeMana().addSaltLog(salt_log,"Accepted_Key")
    return salt_log

def syncModules2Minion(minionName,node_id,region):
    salt_server=settings.C2_STATIC["Salt"]
    try:
	LOG=c2_ssh.conn2(salt_server,CMD_SYNC_MASTER % minionName)
	if "_error_" in LOG:
	    state="ERROR"
    except Exception,ex:
	print Exception,"syncModules2Minion:",ex
	LOG="syncModules2Minion exception:%s" % str(ex)
	ComputeNodeMana().updateMinionState("SYNC_ERROR",node_id,region)
    salt_log="Master sync all(host:%s):%s" % (minionName,LOG)
    ComputeNodeMana().addSaltLog(salt_log,"SYNC_ALL")
    return salt_log
