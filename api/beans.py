from django.conf import settings
from django.db import connections
from django.db import connection
from public import NOVA_DB,NEUTRON_DB,NOVA,NEUTRON


UPDATE_USER_PWD="""
UPDATE user SET password=%s WHERE id=%s
"""

class C2Keystone:
    def chgPwd(self,userid,pwd):
	try:
	    conn=connections["KEYSTONE_Master"]
	    cursor=conn.cursor()
            cursor.execute(UPDATE_USER_PWD,(pwd,userid))
	    conn.commit()
        except Exception,ex:
            print Exception,":",ex
            return False
    	finally:
	    conn.close()
            cursor.close()
   	return True

class ComputeNode:
	def __init__(self,vcpus,memory_mb,vcpus_used,memory_mb_used,hypervisor_hostname,running_vms,deleted=0,host_ip=None,id=None):
		self.vcpus=vcpus
                self.memory_mb=memory_mb
		self.vcpus_used=vcpus_used
		self.memory_mb_used=memory_mb_used
		self.hypervisor_hostname=hypervisor_hostname
		self.running_vms=running_vms
		self.rest_vcpus=vcpus*4-vcpus_used
		self.rest_memory_mb=memory_mb-memory_mb_used
		self.deleted=deleted
		self.host_ip=host_ip
		self.id=id
	def __str__(self):
		return "--host:%s,rest_vcpus:%s,rest_mem:%s-- " % (self.hypervisor_hostname,self.rest_vcpus,self.rest_memory_mb)

        def __repr__(self):
                return "--host:%s,rest_vcpus:%s,rest_mem:%s-- " % (self.hypervisor_hostname,self.rest_vcpus,self.rest_memory_mb)

	def availability(self,cpu,mem):
		return self.rest_vcpus>cpu and self.rest_memory_mb>mem

GET_PHYSICAL="SELECT vcpus,memory_mb,vcpus_used,memory_mb_used,hypervisor_hostname,running_vms FROM compute_nodes WHERE deleted=0 AND host_ip=%s"

GET_ALL_PHYSICAL="SELECT vcpus,memory_mb,vcpus_used,memory_mb_used,hypervisor_hostname,running_vms FROM compute_nodes WHERE deleted=0"

ALL_PHYSICAL="SELECT vcpus,memory_mb,vcpus_used,memory_mb_used,hypervisor_hostname,running_vms,deleted,host_ip,id FROM compute_nodes"

GET_SALT_PHYSICAL="SELECT compute_node_ip,compute_node_host,region,running_vms,node_deleted,id FROM salt_nodes WHERE region=%s"

GET_FILTER_PHYSICAL="""SELECT vcpus,memory_mb,vcpus_used,memory_mb_used,hypervisor_hostname,running_vms FROM compute_nodes WHERE deleted=0 AND hypervisor_hostname IN (%s)"""

ADD_Minion="""
INSERT INTO salt_nodes(id,compute_node_ip,compute_node_host,region,running_vms,salt_state,node_deleted,update_time) VALUES (%s,%s,%s,%s,%s,"INIT",%s,now())
"""

UPDATE_MINION_VMS="""
UPDATE salt_nodes SET running_vms=%s,node_deleted=%s WHERE id=%s AND region=%s
"""

UPDATE_MINION_STATE="""
UPDATE salt_nodes SET salt_state=%s WHERE id=%s AND region=%s
"""

SALT_LOG="""
INSERT INTO salt_thread_log(log,create_time,type) VALUES (%s,now(),%s)
"""

class ComputeNodeMana:

    def getComputeNodeByIp(self,ip,db):
	cursor=db.cursor()
	cursor.execute(GET_PHYSICAL,ip)
	result=cursor.fetchone()
	cursor.close()
	if not result:
		print "Can't find physical machine by ip(%s)" % ip
		return None
	vcpus=result[0]
	memory_mb=result[1]
	vcpus_used=result[2]
	memory_mb_used=result[3]
	hypervisor_hostname=result[4]	
	running_vms=result[5]
	computeNode=ComputeNode(vcpus,memory_mb,vcpus_used,memory_mb_used,hypervisor_hostname,running_vms)
	return computeNode

    def updateMinion(self,vms,deleted,_id,region):
	cursor=connection.cursor()
	cursor.execute(UPDATE_MINION_VMS,(vms,deleted,_id,region))
	cursor.close()

    def updateMinionState(self,state,_id,region):
	cursor=connection.cursor()
	cursor.execute(UPDATE_MINION_STATE,(state,_id,region))
	cursor.close()

    def addMinion(self,n,region):
	cursor=connection.cursor()
	try:
	    cursor.execute(ADD_Minion,(n.id,n.host_ip,n.hypervisor_hostname,region,n.running_vms,n.deleted))
	except Exception,ex:
	    print Exception,":",ex
	    return False
	finally:
	    cursor.close()
	return True

    def addSaltLog(self,log,Type):
	cursor=connection.cursor()
	try:
	    cursor.execute(SALT_LOG,(log,Type,))
	except Exception,ex:
	    print Exception,":",ex
	    return False
	finally:
	    cursor.close()
	return True


    def getComputeNodes(self,db):
	cursor=db.cursor()
	cursor.execute(GET_ALL_PHYSICAL)
	results=cursor.fetchall()
	nodes=[]
	for line in results:
		vcpus=line[0]
		memory_mb=line[1]
		vcpus_used=line[2]
		memory_mb_used=line[3]
		hypervisor_hostname=line[4]	
		running_vms=line[5]
		nodes.append(ComputeNode(vcpus,memory_mb,vcpus_used,memory_mb_used,hypervisor_hostname,running_vms))
	cursor.close()
	return nodes

    def getAllComputeNodes(self,db):
	cursor=db.cursor()
	cursor.execute(ALL_PHYSICAL)
	results=cursor.fetchall()
	nodes=[]
	for line in results:
		vcpus=line[0]
		memory_mb=line[1]
		vcpus_used=line[2]
		memory_mb_used=line[3]
		hypervisor_hostname=line[4]	
		running_vms=line[5]
		deleted=line[6]
		host_ip=line[7]
		_id=line[8]
		nodes.append(ComputeNode(vcpus,memory_mb,vcpus_used,memory_mb_used,hypervisor_hostname,running_vms,deleted,host_ip,_id))
	cursor.close()
	return nodes

    def getSaltComputeNodes(self,region):
	cursor=connection.cursor()
	cursor.execute(GET_SALT_PHYSICAL,(region,))
	results=cursor.fetchall()
	cursor.close()
	nodes={}
	for line in results:
		minion={}
		minion["compute_node_ip"]=line[0]
		minion["compute_node_host"]=line[1]
		minion["region"]=line[2]
		minion["running_vms"]=line[3]
		minion["node_deleted"]=line[4]
		minion["id"]=line[5]
		nodes["%s_%d" % (line[1],minion["id"])]=minion
	return nodes

    def getFilterComputeNodes(self,db,filters):
	cursor=db.cursor()
	in_p=', '.join(list(map(lambda x: '%s', filters)))
	sql=GET_FILTER_PHYSICAL % in_p
	cursor.execute(sql,filters)
	results=cursor.fetchall()
	nodes=[]
	for line in results:
		vcpus=line[0]
		memory_mb=line[1]
		vcpus_used=line[2]
		memory_mb_used=line[3]
		hypervisor_hostname=line[4]	
		running_vms=line[5]
		nodes.append(ComputeNode(vcpus,memory_mb,vcpus_used,memory_mb_used,hypervisor_hostname,running_vms))
	cursor.close()
	return nodes



VIR_PORT="SELECT port_id FROM ipallocations WHERE ip_address=%s"

GET_PORTID_BY_DEVICEID="SELECT id FROM ports WHERE device_id=%s"

VIR_UUID="SELECT device_id FROM ports WHERE id=%s"

GET_INSTANCE="SELECT uuid,memory_mb,vcpus,vm_state,host,user_id,project_id,hostname,id FROM instances WHERE uuid=%s"

PHY_CHILDS="SELECT uuid,memory_mb,vcpus,vm_state,host,user_id,project_id,hostname,id FROM instances WHERE `host`=%s AND vm_state <> 'deleted'"

GET_HOST_IP="""
SELECT instances.`host`,compute_nodes.host_ip,instances.id FROM instances LEFT JOIN compute_nodes ON instances.`host`=compute_nodes.hypervisor_hostname WHERE uuid=%s
"""
COUNT_USER_INST="""
SELECT COUNT(*) FROM instances WHERE vm_state NOT IN ("rescued","resized","error","deleted") AND user_id=%s
"""
class InstanceBean:
	def __init__(self,uuid,memory_mb,vcpus,vm_state,host,user_id,project_id,hostname,id_):
		self.uuid=uuid
		self.memory_mb=memory_mb
		self.vcpus=vcpus
		self.vm_state=vm_state
		self.host=host
		self.user_id=user_id
		self.project_id=project_id
		self.hostname=hostname
		self.id=id_

        def __repr__(self):
                return "--id,%s,uuid:%s,hostname:%s,vcpus:%s,mem:%s-- " % (self.id,self.uuid,self.hostname,self.vcpus,self.memory_mb)

class InstanceManager:

	def getUserInstCount(self,nova_db,userid):
		cursor=nova_db.cursor()
		cursor.execute(COUNT_USER_INST,userid)
		result=cursor.fetchone()
		cursor.close()
		if not result:
			print "Can't find instances  by userid(%s)" % userid
			return 0
		return int(result[0])
	
	def getHostIp(self,nova_db,uuid):
		cursor=nova_db.cursor()
		cursor.execute(GET_HOST_IP,uuid)
		result=cursor.fetchone()
		cursor.close()
		obj={}
		if not result:
			print "Can't find host ip by uuid(%s)" % uuid
			return None
		obj["host"]=result[0]
		obj["host_ip"]=result[1]
		obj["id"]=result[2]
		return obj

	def findPortIdByDevid(self,neutron_db,device_id):
		cursor=neutron_db.cursor()
		cursor.execute(GET_PORTID_BY_DEVICEID,device_id)
		result=cursor.fetchone()
		cursor.close()
		return None if not result else result[0]

	def findInstanceIdByIp(self,neutron_db,nova_db,ip):
		cursor=neutron_db.cursor()
		cursor.execute(VIR_PORT,ip)
		result=cursor.fetchone()
		
		size=0 if not result else len(result)
		if size>0:
		    print "GET PORT_ID %s" % result[0]
		    cursor.execute(VIR_UUID,result[0])
		    result=cursor.fetchone()
		    size=0 if not result else len(result)
		else:
		    print "Can't find port_id by ip(%s),break!" % ip
		cursor.close()
		if size==0:
		    print "Can't find device_id by ip(%s),break!" % ip
		    return None
		uuid=result[0]
		print "GET UUID %s" % uuid
		cur=nova_db.cursor()
		cur.execute(GET_INSTANCE,uuid)
		result=cur.fetchone()
		cur.close()
		if not result:
			print "Can't find instance by device_id(%s),break!" % uuid
			return None
		uuid=result[0]
		memory_mb=result[1]
		vcpus=result[2]
		vm_state=result[3]
		host=result[4]
		user_id=result[5]
		project_id=result[6]
		hostname=result[7]
		id_=result[8]
	        instanceBean=InstanceBean(uuid,memory_mb,vcpus,vm_state,host,user_id,project_id,hostname,id_)
		return instanceBean

	def getChildrens(self,nova_db,ip):
		node=ComputeNodeMana().getComputeNodeByIp(ip,nova_db)
		if not node:
			return None
		host=node.hypervisor_hostname
		cursor=nova_db.cursor()
		cursor.execute(PHY_CHILDS,host)
		childs=[]
		results=cursor.fetchall()
		for result in results:
			uuid=result[0]
			memory_mb=result[1]
			vcpus=result[2]
			vm_state=result[3]
			host=result[4]
			user_id=result[5]
			project_id=result[6]
			hostname=result[7]
			id_=result[8]
	        	instanceBean=InstanceBean(uuid,memory_mb,vcpus,vm_state,host,user_id,project_id,hostname,id_)
			childs.append(instanceBean)
		cursor.close()
		return childs
		

GET_SERVICE_URL='SELECT url FROM endpoint WHERE interface="public" AND region=%s AND service_id =(SELECT id FROM service WHERE type=%s)'
		
class KeyStoneManager:
    def getServiceUrl(self,service_name,region,tenant=settings.SYS_C2):
	print "getServiceUrl:  region:%s,service_name:%s" % (region,service_name)
	db_region=connections["KEYSTONE"]
	cursor=db_region.cursor()
	cursor.execute(GET_SERVICE_URL,(region,service_name))
	result=cursor.fetchone()
	cursor.close()
	return None if not result else result[0] % tenant

GET_FREE_IP='SELECT networks.`name`,networks.`status`,subnets.id,ipavailabilityranges.first_ip,ipavailabilityranges.last_ip,networks.id,subnets.`name` as "subnet_name" FROM ipavailabilityranges,ipallocationpools,subnets,networks WHERE ipavailabilityranges.allocation_pool_id=ipallocationpools.id AND ipallocationpools.subnet_id=subnets.id AND subnets.network_id=networks.id AND networks.`status`="ACTIVE" AND networks.admin_state_up=1 AND networks.shared=1 ORDER BY networks.`name`,subnets.`name`'

GET_ALL_NETWORKS='SELECT id,name,status FROM networks WHERE `status`="ACTIVE" AND admin_state_up=1 AND shared=1'


class NetWork:
	def __init__(self,id_,name,status,subnet=None,subnet_id=None,first_ip="",last_ip=""):
		self.name=name
		self.status=status
		self.subnet=subnet
		self.subnet_id=subnet_id
		self.first_ip=first_ip
		self.last_ip=last_ip
		self.id=id_
		if subnet:
		    self.freeNumber=self.freeNum()

	def freeNum(self):
		index=self.first_ip.rindex(".")+1
		first_num=int(self.first_ip[index:])
		index=self.last_ip.rindex(".")+1
		last_num=int(self.last_ip[index:])
		return last_num-first_num+1

class NetWorkManager:

    def getFreeIp(self,db):
	cursor=db.cursor()
	cursor.execute(GET_FREE_IP)
	results=cursor.fetchall()
	cursor.close()
	nodes=[]
	for line in results:
		name=line[0]
		status=line[1]
		subnet_id=line[2]
		first_ip=line[3]
		last_ip=line[4]	
		id_=line[5]
		subnet=line[6]
		nodes.append(NetWork(id_,name,status,subnet,subnet_id,first_ip,last_ip))
	return nodes

    def getTotalNum(self,nodes):
	display={}
	rtn={}
	for node in nodes:
	    if display.has_key(node.name):
		total=display.get(node.name)
		total+=node.freeNum()
		display[node.name]=total
	    else:
		display[node.name]=node.freeNum()
	    rtn[node.name]={"freeNum":display[node.name],"network_id":node.id}
	return rtn

    def getAllNetWorks(self,db):
	cursor=db.cursor()
	cursor.execute(GET_ALL_NETWORKS)
	results=cursor.fetchall()
	cursor.close()
	nodes=[]
	for line in results:
		id_=line[0]
		name=line[1]
		status=line[2]
		nodes.append(NetWork(id_,name,status))
	return nodes

    def getAllTotalNum(self,nodes,db):
	freeNodes=self.getTotalNum(nodes)
	networks=self.getAllNetWorks(db)
	for network in networks:
	    if not freeNodes.has_key(network.name):
		freeNodes[network.name]={"freeNum":0,"network_id":network.id}
	return freeNodes

GET_IP_BY_UUID="""
	SELECT ports.id,ipallocations.ip_address,ipallocations.network_id,networks.`name` 
	FROM ports LEFT JOIN ipallocations ON ports.id=ipallocations.port_id
	LEFT JOIN networks ON ports.network_id=networks.id
	WHERE ports.device_id=%s
"""

GET_IP_BY_UUID_NETID="""
	SELECT ports.id,ipallocations.ip_address,ipallocations.network_id,networks.`name` 
	FROM ports LEFT JOIN ipallocations ON ports.id=ipallocations.port_id
	LEFT JOIN networks ON ports.network_id=networks.id
	WHERE ports.device_id=%s AND ports.network_id=%s
"""

class NetworkFlowManager:
    def getNetInfoByUUID(self,uuid,db_region):
	cursor=db_region.cursor()
	cursor.execute(GET_IP_BY_UUID,uuid)
	result=cursor.fetchall()
	cursor.close()
	nodes=[]
	for line in results:
		obj={}
		obj["id"]=line[0]
		obj["ip_address"]=line[1]
		obj["network_id"]=line[2]
		obj["network_name"]=line[3]
		nodes.append(obj)
	return nodes

    def getNetInfoByUUIDAndNetId(self,db_region,uuid,network_id):
	cursor=db_region.cursor()
	cursor.execute(GET_IP_BY_UUID_NETID,(uuid,network_id))
	result=cursor.fetchone()
	cursor.close()
	if not result:
		print "Can't find network info by device_id(%s),break!" % uuid
		return None
	obj={}
	obj["id"]=result[0]
	obj["ip_address"]=result[1]
	obj["network_id"]=result[2]
	obj["network_name"]=result[3]
	return obj


ADD_EVA_LOG="""
INSERT INTO c2_eva_log(`user`,eva_ip,output,remote_ip) VALUES (%s,%s,%s,%s)
"""

class EvaLog:
    def addLog(self,user,eva_ip,output,remote_ip):
	cursor=connection.cursor()
	try:
	    cursor.execute(ADD_EVA_LOG,(user,eva_ip,output,remote_ip))
	except Exception,ex:
	    print Exception,"ADD_EVA_LOG:",ex
	    return False
	finally:
	    cursor.close()
	return True

ADD_NET_FLOW="""
INSERT INTO c2_network_flow(`uuid`,`network_flow`,`region`,`network_id`) VALUES (%s,%s,%s,%s)
"""

GET_NET_FLOWS="""
SELECT network_flow,network_id FROM c2_network_flow WHERE uuid=%s AND region=%s
"""

ADD_SU_LOG="""
INSERT INTO c2_su_log(`uuid`,`region`,`network_id`,`network_name`,`action`,`log`) VALUES (%s,%s,%s,%s,%s,%s)
"""

class NetWorkFlow:
    def addNetWorkFlow(self,uuid,network_flow,region,network_id):
	cursor=connection.cursor()
	try:
	    cursor.execute(ADD_NET_FLOW,(uuid,network_flow,region,network_id))
	except Exception,ex:
	    print Exception,":",ex
	    return False
	finally:
	    cursor.close()
	return True

    def getNetWorkFlows(self,uuid,region):
	cursor=connection.cursor()
	cursor.execute(GET_NET_FLOWS,(uuid,region))
	results=cursor.fetchall()
	cursor.close()
	nodes=[]
	for line in results:
		obj={}
		obj["network_flow"]=line[0]
		obj["network_id"]=line[1]
		obj["uuid"]=uuid
		obj["region"]=region
		nodes.append(obj)
	return nodes

    def addLog(self,uuid,region,network_id,network_name,log,action):
	cursor=connection.cursor()
	try:
	    cursor.execute(ADD_SU_LOG,(uuid,region,network_id,network_name,action,log))
	except Exception,ex:
	    print Exception,"ADD_SU_LOG:",ex
	    return False
	finally:
	    cursor.close()
	return True
		
	
C2_CIDR_GET="""
SELECT id,cidr,tenant_id,network_id,region FROM c2_cidr_allocation WHERE tenant_id=%s AND region=%s OR tenant_id is NULL AND    region =%s ORDER BY tenant_id DESC,id ASC limit 1
"""
C2_CIDR_UPDATE="""
UPDATE c2_cidr_allocation SET tenant_id=%s,network_id=%s WHERE id=%s AND region=%s 
"""

class C2cidrManager:
    def getFreecidr(self,tenant_id,region):
	cursor=connection.cursor()
	cursor.execute(C2_CIDR_GET,(tenant_id,region,region))
	result=cursor.fetchone()
	cursor.close()
	if not result:
	    print "Can't find cidr "
	    return None
	obj={}
	obj["id"]=result[0]
	obj["cidr"]=result[1]
	obj["tenantid"]=result[2]
	obj["network_id"]=result[3]
	obj["region"]=result[4]
	return obj


    def useCidr(self,id_,tenantid,network_id,region):
	cursor=connection.cursor()
	try:
	    cursor.execute(C2_CIDR_UPDATE,(tenantid,network_id,id_,region))
	except Exception,ex:
	    print Exception,":",ex
	    return False
	finally:
	    cursor.close()
	return True

		

		

		












