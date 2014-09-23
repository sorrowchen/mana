from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    #url(r'su/relimit/(?P<region>[\w-]+)/(?P<uuid>[\w-]+)/(?P<action>[\w-]+)/$','api.su.relimit'),
    #url(r'test/$','api.eva.test'),
    url(r'init/$','minions.views.init'),
)

