from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.ip.views import index,vrf_index

urlpatterns = patterns ( "",
        (r"^$",                   login_required(index)),
        (r"^(?P<vrf_id>\d+)/$",   login_required(vrf_index)),
        (r"^(?P<vrf_id>\d+)/(?P<prefix>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}/\d{1,2})/$",   login_required(vrf_index)),
)
