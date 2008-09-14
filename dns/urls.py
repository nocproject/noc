from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.dns.views import zone

urlpatterns = patterns ( "",
    (r"(?P<zone>[a-zA-Z0-9\-.]+)/zone/(?P<ns_id>\d+)/",         login_required(zone)),
)
