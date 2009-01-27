from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.fm.views import index,event

urlpatterns = patterns ( "",
    (r"^(?P<event_id>\d+)/$", login_required(event)),
    (r"^$",                   login_required(index)),
)
