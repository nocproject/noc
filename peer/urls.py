from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.peer.views import as_rpsl,as_set_rpsl,as_dot

urlpatterns = patterns ( "",
    (r"^AS/(?P<asn>\d+)/rpsl/",                  login_required(as_rpsl)),
    (r"^AS/(?P<asn>\d+)/dot/",                  login_required(as_dot)),
    (r"^AS-SET/(?P<as_set>AS-[A-Z0-9\-]+)/rpsl/", login_required(as_set_rpsl)),
)
