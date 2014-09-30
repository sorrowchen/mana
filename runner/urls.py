from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'init/$','runner.views.init'),
)


from runner.startup import sys_startup

#sys_startup()
