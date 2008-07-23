from django.conf.urls.defaults import *

handler404="noc.main.views.handler404"

urlpatterns = patterns('',
    # For debugging purposes only. Overriden by lighttpd/apache
     (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'static'}),
    # 
     (r'^$',      include('noc.main.urls')),
     (r'^admin/', include('django.contrib.admin.urls')),
     (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name':'template/login.html'}),
     (r'^main/',  include('noc.main.urls')),
     (r"^ip/", include("noc.ip.urls")),
)
