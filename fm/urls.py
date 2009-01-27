from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.fm.views import index,event,reclassify,create_rule

urlpatterns = patterns ( "",
    (r"^(?P<event_id>\d+)/reclassify/$", login_required(reclassify)),
    (r"^(?P<event_id>\d+)/create_rule/$", login_required(create_rule)),
    (r"^(?P<event_id>\d+)/$", login_required(event)),
    (r"^$",                   login_required(index)),
)
