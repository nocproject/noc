# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Application class
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import logging
import os
import datetime
## Django modules
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect,\
                        HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.db import connection
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils.html import escape
from django.template import loader
## NOC modules
from access import HasPerm, Permit, Deny
from site import site
from noc.lib.forms import NOCForm
from noc import settings
from noc.lib.serialize import json_encode, json_decode
from noc.sa.interfaces import DictParameter


def view(url, access, url_name=None, menu=None, method=None, validate=None,
         api=False):
    """
    @view decorator
    :param url: URL relative to application root
    :param access:
    :param url_name:
    :param menu:
    :param method:
    :param validate: Form class or callable to check input
    :param api: Does the view exposed as API function
    """

    def decorate(f):
        f.url = url
        f.url_name = url_name
        # Process access
        if type(access) == bool:
            f.access = Permit() if access else Deny()
        elif isinstance(access, basestring):
            f.access = HasPerm(access)
        else:
            f.access = access
        f.menu = menu
        f.method = method
        f.api = api
        if type(validate) == dict:
            f.validate = DictParameter(attrs=validate)
        else:
            f.validate = validate
        return f

    return decorate


class ApplicationBase(type):
    """
    Application metaclass. Registers application class to site
    """

    def __new__(cls, name, bases, attrs):
        global site
        m = type.__new__(cls, name, bases, attrs)
        if "apps" in m.__module__:
            site.register(m)
        return m


class Application(object):
    """
    Basic application class.
    
    Application combined by set of methods, decorated with @view.
    Each method accepts requests and returns reply
    """
    __metaclass__ = ApplicationBase
    title = "APPLICATION TITLE"
    icon = "icon_application"
    extra_permissions = []  # List of additional permissions, not related with views
    implied_permissions = {}  # permission -> list of implied permissions

    Form = NOCForm  # Shortcut for form class
    config = settings.config

    def __init__(self, site):
        self.site = site
        parts = self.__class__.__module__.split(".")
        self.module = parts[1]
        self.app = parts[3]
        self.module_title = __import__("noc.%s" % self.module, {}, {},
            ["MODULE_NAME"]).MODULE_NAME
        self.app_id = "%s.%s" % (self.module, self.app)
        self.menu_url = None   # Set by site.autodiscover()

    @property
    def js_app_class(self):
        return "NOC.main.desktop.IFramePanel"

    def get_launch_info(self, user):
        """
        Return desktop launch information
        """
        from noc.main.models import Permission

        ps = self.get_app_id().replace(".", ":") + ":"
        if user.is_superuser:
            qs = Permission.objects
        else:
            qs = user.noc_user_permissions
        perms = [p.split(":")[2] for p in
                 qs.filter(name__startswith = ps).values_list("name",
                                                              flat=True)]
        return {
            "class": self.js_app_class,
            "title": unicode(self.title),
            "params": {
                "url": self.menu_url,
                "permissions": perms
            }
        }

    @classmethod
    def get_app_id(cls):
        """
        Returns application id
        """
        parts = cls.__module__.split(".")
        return "%s.%s" % (parts[1], parts[3])

    @property
    def base_url(self):
        """
        Application's base URL
        """
        return "/%s/%s/" % (self.module, self.app)

    def reverse(self, url, *args, **kwargs):
        """
        Reverse URL name to URL
        """
        return self.site.reverse(url, *args, **kwargs)

    def message_user(self, request, message):
        """
        Send a message to user
        """
        messages.info(request, unicode(message))

    def get_template_path(self, template):
        """
        Return path to named template
        """
        if isinstance(template, basestring):
            template = [template]
        r = []
        for t in template:
            r += [
                os.path.join(self.module, "apps", self.app, "templates", t),
                os.path.join(self.module, "templates", t),
                os.path.join("templates", t)
            ]
        return r

    def get_object_or_404(self, *args, **kwargs):
        """
        Shortcut to get_object_or_404
        """
        return get_object_or_404(*args, **kwargs)

    def render(self, request, template, dict={}, **kwargs):
        """
        Render template within context
        """
        return render_to_response(self.get_template_path(template),
                                  dict if dict else kwargs,
                                  context_instance=RequestContext(request,
                                                                  dict={
                                                                      "app": self}))

    def render_template(self, template, dict={}, **kwargs):
        """
        Render template to string
        """
        tp = self.get_template_path(template)
        return loader.render_to_string(tp, dict or kwargs)

    def render_response(self, data, content_type="text/plain"):
        """
        Render arbitrary Content-Type response
        """
        return HttpResponse(data, content_type=content_type)

    def render_plain_text(self, text, mimetype="text/plain"):
        """
        Render plain/text response
        """
        return HttpResponse(text, mimetype=mimetype)

    def render_json(self, obj, status=200):
        """
        Create serialized JSON-encoded response
        """
        return HttpResponse(json_encode(obj),
                            mimetype="text/json", status=status)

    def render_success(self, request, subject=None, text=None):
        """
        Render "success" page
        """
        return self.site.views.main.message.success(request, subject=subject,
                                                    text=text)

    def render_failure(self, request, subject=None, text=None):
        """
        Render "failure" page
        """
        return self.site.views.main.message.failure(request, subject=subject,
                                                    text=text)

    def render_wait(self, request, subject=None, text=None, url=None, timeout=5,
                    progress=None):
        """
        Render wait page
        """
        return self.site.views.main.message.wait(request, subject=subject,
                                                 text=text, timeout=timeout,
                                                 url=url, progress=progress)

    def response_redirect(self, url, *args, **kwargs):
        """
        Redirect to URL
        """
        if ":" in url:
            url = self.reverse(url, *args, **kwargs)
        return HttpResponseRedirect(url)

    def response_redirect_to_referrer(self, request, back_url=None):
        """
        Redirect to referrer page
        """
        if back_url is None:
            back_url = self.base_url
        return self.response_redirect(
            request.META.get("HTTP_REFERER", back_url))

    def response_redirect_to_object(self, object):
        """
        Redirect to object: {{base.url}}/{{object.id}}/
        """
        return self.response_redirect("%s%d/" % (self.base_url, object.id))

    def response_forbidden(self, text=None):
        """
        Render Forbidden response
        """
        return HttpResponseForbidden(text)

    def response_not_found(self, text=None):
        """
        Render Not Found response
        """
        return HttpResponseNotFound(text)

    def response_bad_request(self, text=None):
        """
        Render 400 Bad Request
        :param text:
        :return:
        """
        return HttpResponse(text, status=400)

    def response_accepted(self, location=None):
        """
        Render 202 Accepted
        :param location:
        :return:
        """
        r = HttpResponse("", status=202)
        if location:
            r["Location"] = location
        return r

    def close_popup(self, request):
        """
        Render javascript closing popup window
        """
        return self.render(request, "close_popup.html")

    def html_escape(self, s):
        """
        Escape HTML
        """
        return escape(s)

    ##
    ## Logging
    ##
    def debug(self, message):
        logging.debug(message)

    def error(self, message):
        logging.error(message)

    def cursor(self):
        """
        Returns db cursor
        """
        return connection.cursor()

    def execute(self, sql, args=[]):
        """
        Execute SQL query
        """
        cursor = self.cursor()
        cursor.execute(sql, args)
        return cursor.fetchall()

    def lookup(self, request, func):
        """
        AJAX lookup wrapper
        @todo: Remove
        """
        result = []
        if request.GET and "q" in request.GET:
            q = request.GET["q"]
            if len(q) > 2:  # Ignore requests shorter than 3 letters
                result = list(func(q))
        return self.render_plain_text("\n".join(result))

    def lookup_json(self, request, func, id_field="id", name_field="name"):
        """
        Ajax lookup wrapper, returns JSON list of hashes
        """
        result = []
        if request.GET and "q" in request.GET:
            q = request.GET["q"]
            for r in func(q):
                result += [{id_field: r, name_field: r}]
        return self.render_json(result)

    def get_views(self):
        """
        Iterator returning application views
        """
        for n in [v for v in dir(self) if hasattr(getattr(self, v), "url")]:
            yield getattr(self, n)

    def get_permissions(self):
        """
        Return a set of permissions, used by application
        """
        prefix = self.get_app_id().replace(".", ":")
        p = set(["%s:launch" % prefix])
        # View permissions from HasPerm
        for view in self.get_views():
            if isinstance(view.access, HasPerm):
                p.add(view.access.get_permission(self))
        # mrt_config permissions
        for mrt in self.mrt_config:
            c = self.mrt_config[mrt]
            if "access" in c:
                if isinstance(c["access"], HasPerm):
                    p.add(c["access"].get_permission(self))
                elif isinstance(c["access"], basestring):
                    p.add("%s:%s" % (prefix, c["access"]))
        # extra_permissions
        if callable(self.extra_permissions):
            extra = self.extra_permissions()
        else:
            extra = self.extra_permissions
        for e in extra:
            p.add(HasPerm(e).get_permission(self))
        return p

    def user_access_list(self, user):
        """
        Return a list of user access entries
        """
        return []

    def group_access_list(self, group):
        """
        Return a list of group access entries
        """
        return []

    def user_access_change_url(self, user):
        """
        Return an URL to change user access
        """
        return None

    def group_access_change_url(self, group):
        """
        Return an URL to change group access
        """
        return None

    def check_mrt_access(self, request, name):
        mc = self.mrt_config[name]
        if "access" not in mc:
            return True
        access = mc["access"]
        if type(access) == bool:
            access = Permit() if access else Deny()
        elif isinstance(access, basestring):
            access = HasPerm(access)
        else:
            access = access
        return access.check(self, request.user)

    @view(url="^mrt/(?P<name>[^/]+)/$", method=["POST"],
          access=True, api=True)
    def api_run_mrt(self, request, name):
        from noc.sa.models import ReduceTask, ManagedObjectSelector

        # Check MRT configured
        if name not in self.mrt_config:
            return self.response_not_found("MRT %s is not found" % name)
        # Check MRT access
        if not self.check_mrt_access(request, name):
            return self.response_forbidden("Forbidden")
        #
        data = json_decode(request.raw_post_data)
        if "selector" not in data:
            return self.response_bad_request("'selector' is missed")
        # Run MRT
        mc = self.mrt_config[name]
        map_params = data.get("map_params", {})
        map_params = dict((str(k), v) for k, v in map_params.iteritems())
        task = ReduceTask.create_task(
            ManagedObjectSelector.resolve_expression(data["selector"]),
            "pyrule:mrt_result", {},
            mc["map_script"], map_params,
            mc.get("timeout", 0)
        )
        return task.id

    @view(url="^mrt/(?P<name>[^/]+)/(?P<task>\d+)/$", method=["GET"],
          access=True, api=True)
    def api_get_mrt_result(self, request, name, task):
        from noc.sa.models import ReduceTask, ManagedObjectSelector

        # Check MRT configured
        if name not in self.mrt_config:
            return self.response_not_found("MRT %s is not found" % name)
        # Check MRT access
        if not self.check_mrt_access(request, name):
            return self.response_forbidden("Forbidden")
        #
        t = self.get_object_or_404(ReduceTask, id=int(task))
        try:
            r = t.get_result(block=False)
        except ReduceTask.NotReady:
            # Not ready
            completed = t.maptask_set.filter(status__in=("C", "F")).count()
            total = t.maptask_set.count()
            return {
                "ready": False,
                "progress": int(completed * 100 / total),
                "max_timeout": (t.stop_time - datetime.datetime.now()).seconds,
                "result": None
            }
        # Return result
        return {
            "ready": True,
            "progress": 100,
            "max_timeout": 0,
            "result": r
        }

    # name -> {access: ..., map_script: ..., timeout: ...}
    mrt_config = {}
