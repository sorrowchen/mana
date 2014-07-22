from django.conf.urls import patterns, include, url


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
    url(r'add-network-flow/(?P<region>[\w-]+)/(?P<uuid>[\w-]+)/(?P<su>[\w-]+)/$','api.su.limitSu'),
)
