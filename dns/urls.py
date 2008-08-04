from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.dns.views import index,zone

urlpatterns = patterns ( "",
    (r"^$",                                      login_required(index)),
    (r"^type/(?P<zonetype>[FR])/$",              login_required(index)),
    (r"(?P<zone>[a-zA-Z0-9\-.]+)/zone/",         login_required(zone)),
)
