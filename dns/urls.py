from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.dns.views import index

urlpatterns = patterns ( "",
    (r"^$",                                      login_required(index)),
    (r"^type/(?P<zonetype>[FR])/$",              login_required(index)),
)
