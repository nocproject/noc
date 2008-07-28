from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.peer.views import index,rpsl

urlpatterns = patterns ( "",
    (r"^$",                   login_required(index)),
    (r"^(?P<asn>\d+)/rpsl/",  login_required(rpsl)),
)
