from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.cm.views import view,text

urlpatterns = patterns ( "",
    (r"^view/(?P<object_id>\d+)/$", login_required(view)),
    (r"^view/(?P<object_id>\d+)/(?P<revision>\d+)/$", login_required(view)),
    
    (r"^view/(?P<object_id>\d+)/text/$", login_required(text)),
)
