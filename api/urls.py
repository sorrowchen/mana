from django.conf.urls import patterns, include, url
from framework import require_login
from su import chgPwd,getUserNetwork,getUserNetwork2,getMultiUserNetwork

urlpatterns = patterns('',
    url(r'index/$','api.views.index'),#get   use:index.html    
    url(r'virs/(?P<region>[\w-]+)/$','api.views.virs'), #get   use:virs.html
    url(r'metric/(?P<region>[\w-]+)/(?P<uuid>[\w-]+)/$','api.metric.index'), #get use:metric.html
    url(r'm1/$','api.metric.m1'), # nothing  use:m1.html
    url(r'statics/(?P<region>[\w-]+)/(?P<Meteric>[\w-]+)/(?P<UUID>[\w-]+)/(?P<duration>[\w-]+)/$','api.metric.statics'),#   get ceilometer data
    url(r'evacuate/(?P<host>[\w-]+)/$','api.views.evacuate'),  #nothing
    url(r'face/$','api.views.face'),# nothing
    url(r'eva/$','api.views.eva'), # nothing
    url(r'chgPwd/(?P<userid>[\w-]+)/(?P<pwd>[\w-]+)/$','api.views.chgPwd'),  #get   change keystone user's pwd?
    url(r'free-res/$','api.eva.getFreeRes'), #get    use:ip_list.html
    url(r'free-res/(\w+)/$','api.eva.getFreeResByRegion'),	#error???????
    url(r'repair-eva/(?P<ip>[\w\.]+)/$','api.eva.controller'),
    url(r'repair-eva/(?P<ip>[\w\.]+)/(?P<region>[\w-]+)/$','api.eva.controller'),
    url(r'machine/([\w\.]+)/$','api.eva.getMachineInfoByIp'),
    url(r'service-status/$','api.eva.getServiceStatus'),	#get
    url(r'az-list/$','api.eva.az_list'),
    url(r'free-ip-list/$','api.eva.ip_list'),  #get   use:ip_list.html
    url(r'ava-network/(?P<region>[\w-]+)/(?P<nets>[\w-]+)/$','api.eva.get_ava_network'),
    url(r'free-ip/(?P<region>[\w-]+)/$','api.eva.ip_list_region'),   #get
    url(r'add-network-flow/(?P<region>[\w-]+)/(?P<uuid>[\w-]+)/(?P<network_flow>[\w-]+)/(?P<network_id>[\w-]+)/$','api.su.limitSu'),
    url(r'su/relimit/(?P<region>[\w-]+)/(?P<uuid>[\w-]+)/(?P<action>[\w-]+)/$','api.su.relimit'),
    url(r'chgPwd/(?P<region>[\w-]+)/(?P<uuid>[\w-]+)/(?P<pwd>[\w-]+)/$',chgPwd),
    url(r'get-user-network/(?P<region>[\w-]+)/(?P<tenant_id>[\w-]+)/(?P<networkname>[=\w-]+)/$',getUserNetwork),
    url(r'get-user-multi-network/(?P<region>[\w-]+)/(?P<tenant_id>[\w-]+)/(?P<networkname>[=\w-]+)/$',getMultiUserNetwork),
    url(r'get-token-network/(?P<region>[\w-]+)/(?P<tenant_id>[\w-]+)/(?P<networkname>[=\w-]+)/$',getUserNetwork2),
    url(r'user-resource-quotas/(?P<region>[\w-]+)/(?P<userid>[\w-]+)/(?P<tenantid>[\w-]+)/$','api.su.getUserStackInfo'),
    url(r'test/$','api.eva.test'),
    url(r'virs_list/(?P<region>[\w-]+)/$','api.alarm.virs_list'),
    url(r'statics/(?P<region>[\w-]+)/(?P<Meteric>[\w-]+)/(?P<UUID>[\w-]+)/seconds/(?P<time>[\w-]+)/$','api.alarm.alarm_statics'),#   get ceilometer data for alarm
    url(r'alarm/(?P<region>[\w-]+)/(?P<time>[\w-]+)/$', 'api.alarm.getAlarmTask'),
)
