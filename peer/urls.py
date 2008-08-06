from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.peer.views import index,as_rpsl,as_dot,as_set_rpsl

urlpatterns = patterns ( "",
    (r"^$",                                      login_required(index)),
    (r"^AS/(?P<asn>\d+)/rpsl/",                  login_required(as_rpsl)),
    (r"^AS/(?P<asn>\d+)/dot/",                  login_required(as_dot)),
    (r"^AS-SET/(?P<as_set>AS-[A-Z0-9\-]+)/rpsl/", login_required(as_set_rpsl)),
)
