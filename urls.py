from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # For debugging purposes only. Overriden by lighttpd/apache
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'static'}),
    # Example:
    # (r'^noc/', include('noc.foo.urls')),
     (r'^admin/', include('django.contrib.admin.urls')),
     (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name':'template/login.html'}),
     (r"^ip/", include("noc.ip.urls")),
)
