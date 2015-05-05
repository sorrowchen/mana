from django.db import connections

NOVA=lambda x:x+"_nova"	
NEUTRON=lambda x:x+"_neutron"

NOVA_DB=lambda x:connections[NOVA(x)]
NEUTRON_DB=lambda x:connections[NEUTRON(x)]

RTN_200="""{"code":200,"message":"ok","data":"%s"}"""
RTN_500="""{"code":500,"message":"%s","data":"None"}"""

TOKEN={"id":"x","expire":"2014-11-11 00:00:00"}

def getConnIp(host_ip):
    #change private to public ip
    compute_nodes_interface={"172.28.2":"172.28.1","172.29.204":"172.29.202","172.30.251":"172.30.250"}
    prex=".".join(host_ip.split(".")[:3])
    if compute_nodes_interface.has_key(prex):
        host_ip=host_ip.replace(prex,compute_nodes_interface[prex])
    return host_ip




