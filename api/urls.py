from django.conf.urls import patterns, include, url
from framework import require_login
from su import chgPwd

urlpatterns = patterns('',
    url(r'index/$','api.views.index'),
    url(r'evacuate/(?P<host>[\w-]+)/$','api.views.evacuate'),
    url(r'face/$','api.views.face'),
    url(r'eva/$','api.views.eva'),
    url(r'free-res/$','api.eva.getFreeRes'),
    url(r'free-res/(\w+)/$','api.eva.getFreeResByRegion'),	
    url(r'repair-eva/([\w\.]+)/$','api.eva.controller'),
    url(r'machine/([\w\.]+)/$','api.eva.getMachineInfoByIp'),
    url(r'service-status/$','api.eva.getServiceStatus'),	
    url(r'az-list/$','api.eva.az_list'),
    url(r'free-ip-list/$','api.eva.ip_list'),
    url(r'ava-network/(?P<region>[\w-]+)/(?P<nets>[\w-]+)/$','api.eva.get_ava_network'),
    url(r'free-ip/(?P<region>[\w-]+)/$','api.eva.ip_list_region'),
    url(r'add-network-flow/(?P<region>[\w-]+)/(?P<uuid>[\w-]+)/(?P<network_flow>[\w-]+)/(?P<network_id>[\w-]+)/$','api.su.limitSu'),
    url(r'su/relimit/(?P<region>[\w-]+)/(?P<uuid>[\w-]+)/(?P<action>[\w-]+)/$','api.su.relimit'),
    url(r'chgPwd/(?P<region>[\w-]+)/(?P<uuid>[\w-]+)/(?P<pwd>[\w-]+)/$',require_login(chgPwd)),
    url(r'test/$','api.eva.test'),
)
