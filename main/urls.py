from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.main.views import index,logout,report,report_index

urlpatterns = patterns ( None,
        (r"^$",        login_required(index)),
        (r"^logout/$", login_required(logout)),
        (r"^report/(?P<report>[a-z0-9\-_.]+)/$", login_required(report)),
        (r"^report/$", login_required(report_index))
)