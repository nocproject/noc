from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.main.views import index,logout

urlpatterns = patterns ( None,
        (r"^$",        login_required(index)),
        (r"^logout/$", login_required(logout)),
)