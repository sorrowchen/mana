from django.db import connections

NOVA=lambda x:x+"_nova"	
NEUTRON=lambda x:x+"_neutron"

NOVA_DB=lambda x:connections[NOVA(x)]
NEUTRON_DB=lambda x:connections[NEUTRON(x)]

RTN_200="""{"code":200,"message":"ok","data":"%s"}"""
RTN_500="""{"code":500,"message":"%s","data":"None"}"""
