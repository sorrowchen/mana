from django.http import HttpResponse
from django.conf import settings

def require_login(view):
    def new_view(req,*args,**kwargs):
	token=req.META.get("HTTP_C2_AUTH_TOKEN",None)
	if not settings.C2_AUTH_TOKEN.has_key(token):
	    return HttpResponse("Unknow auth token(%s) request." % token)
	return view(request,*args,**kwargs)
    return new_view
