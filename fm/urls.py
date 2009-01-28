from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.fm.views import index,event,reclassify,create_rule,event_list_css

urlpatterns = patterns ( "",
    (r"^(?P<event_id>\d+)/reclassify/$", login_required(reclassify)),
    (r"^(?P<event_id>\d+)/create_rule/$", login_required(create_rule)),
    (r"^(?P<event_id>\d+)/$", login_required(event)),
    (r"^event_list_css/$",    login_required(event_list_css)),
    (r"^$",                   login_required(index)),
)
