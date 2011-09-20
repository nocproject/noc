# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Site implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import types
import glob
import os
import urllib
import hashlib
## Django modules
from django.http import HttpResponse, HttpResponseRedirect,\
                        HttpResponseNotFound, HttpResponseForbidden,\
                        HttpResponseServerError
from django.utils.http import urlquote
from django.conf.urls.defaults import *
from django.core.urlresolvers import *
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.simplejson.encoder import JSONEncoder
## NOC modules
from noc.settings import INSTALLED_APPS
from noc.lib.debug import get_traceback


class DynamicMenu(object):
    title = "DYNAMIC MENU"

    @property
    def items(self):
        """
        Generator yielding (title, url, access)
        """
        raise StopIteration


class ProxyNode:
    pass

HTTP_METHODS = set(["GET", "POST", "PUT", "DELETE"])

class URL(object):
    """
    URL Data wrapper
    """
    def __init__(self, url, name=None, method=None):
        self.url = url
        self.name = name
        if method is None:
            self.method = HTTP_METHODS
        else:
            if isinstance(method, basestring):
                method = [method]
            if type(method) not in (types.ListType, types.TupleType):
                raise TypeError("Invalid type for 'method'")
            for m in method:
                if m not in HTTP_METHODS:
                    raise ValueError("Invalid method '%s'" % m)
            self.method = set(method)

    def __repr__(self):
        return "<URL %s>" % unicode(self)

    def __unicode__(self):
        s = self.url
        if self.name:
            s += ", name='%s'" % self.name
        return s


class Site(object):
    """
    Application site. Registers applications, builds menu and
    handling views
    """
    def __init__(self):
        self.apps = {}  # app_id -> app instance
        self.urlpatterns = patterns("")
        self.urlresolvers = {}  # (module,appp) -> RegexURLResolver
        self.menu = []
        self.menu_index = {}  # id -> menu item
        self.reports = []  # app_id -> title
        self.views = ProxyNode()  # Named views proxy
        self.testing_mode = hasattr(settings, "IS_TEST")

    @property
    def urls(self):
        """
        Returns URLConf
        """
        return self.urlpatterns

    def register_named_view(self, mod_ns, app_ns, name, view):
        """
        Register named application view
        """
        if not hasattr(self.views, mod_ns):
            setattr(self.views, mod_ns, ProxyNode())
        n = getattr(self.views, mod_ns)
        if not hasattr(n, app_ns):
            setattr(n, app_ns, ProxyNode())
        n = getattr(n, app_ns)
        setattr(n, name, view)

    def view_urls(self, view):
        """
        Generator returning view's URL objects
        """
        if isinstance(view.url, basestring):  # view.url is string type
            yield URL(view.url,
                      name=getattr(view, "url_name", None),
                      method=getattr(view, "method", None))
        elif isinstance(view.url, URL):  # Explicit URL object
            yield view.url
        elif (isinstance(view.url, types.ListType) or
              isinstance(view.url, types.TupleType)):  # List type
            for o in view.url:
                if isinstance(o, basestring):  # Given by string
                    yield URL(o)
                elif isinstance(o, URL):
                    yield o
                else:
                    raise Exception("Invalid URL object: %s" % str(o))
        else:
            raise Exception("Invalid URL object: %s" % str(view.url))

    def site_access(self, app, view):
        """
        Curry application with access
        """
        return lambda user: view.access.check(app, user)

    def site_view(self, app, view_map):
        """
        Decorator for application view
        """
        # Render view
        def inner(request, *args, **kwargs):
            try:
                v = view_map[request.method]
            except KeyError:
                return HttpResponseNotFound("No handler for '%s' method" % request.method)
            if not request.user or not v.access.check(app, request.user):
                return HttpResponseForbidden()
            if v.validate:
                if issubclass(v.validate, Form):
                    f = v.validate(request.GET)
                    if f.is_valid():
                        kwargs.update(f.cleaned_data)
                    else:
                        r = JSONEncoder(ensure_ascii=False).encode({
                            "status": False,
                            "error": f.errors
                        })
                        return HttpResponse(r, status=400,  # BAD REQUEST
                                            mimetype="text/json; charset=utf-8")
            try:
                r = v(request, *args, **kwargs)
            except PermissionDenied, why:
                return HttpResponseForbidden(why)
            except:
                # Generate 500
                r = HttpResponseServerError(content=get_traceback())
            if not isinstance(r, HttpResponse):
                try:
                    return HttpResponse(JSONEncoder(ensure_ascii=False).encode(r),
                                        mimetype="text/json; charset=utf-8")
                except:
                    return HttpResponse(get_traceback(), status=500)
            else:
                return r

        from access import PermissionDenied
        from django.forms import Form
        return inner

    def add_to_menu(self, app, v):
        if callable(v.menu):
            menu = v.menu(app)
        else:
            menu = v.menu
        if not menu:
            return
        path = [app.module]
        parts = [x.strip() for x in menu.split("|")]
        root = self.menu[-1]
        while len(parts) > 1:
            p = parts.pop(0)
            path += [p]
            exists = False
            for n in root["children"]:
                if p == n["title"]:
                    exists = True
                    break
            if exists:
                root = n
            else:
                r = {"title": p, "children": []}
                self.set_menu_id(r, path)
                root["children"] += [r]
                root = r
        path += parts
        app.menu_url = ("/%s/%s/%s" % (app.module, app.app,
                                       v.url[1:])).replace("$", "")
        r = {
            "title": parts[0],
            "app": app,
            "access": self.site_access(app, v)
        }
        self.set_menu_id(r, path)
        root["children"] += [r]

    def add_app_menu(self, app):
        if not self.menu:
            # Started without autodiscover
            # Add module menu
            self.add_module_menu(app.get_app_id().split(".")[0])
        root = self.menu[-1]
        path = [app.module]
        parts = [x.strip() for x in unicode(app.menu).split("|")]
        while len(parts) > 1:
            p = parts.pop(0)
            path += [p]
            exists = False
            for n in root["children"]:
                if p == n["title"]:
                    exists = True
                    break
            if exists:
                root = n
            else:
                r = {"title": p, "children": []}
                self.set_menu_id(r, path)
                root["children"] += [r]
                root = r
        path += parts
        r = {
            "title": parts[0],
            "app": app,
            "access": lambda user: app.launch_access.check(app, user)
        }
        self.set_menu_id(r, path)
        root["children"] += [r]

    def register(self, app_class):
        """
        Register application class
        Fetch all view_* methods
        And register them
        """
        # Register application
        app_id = app_class.get_app_id()
        if app_id in self.apps:
            raise Exception("Application %s is already registered" % app_id)
        # Initialize application
        app = app_class(self)
        self.apps[app_id] = app
        # Install module URL resolver
        try:
            mr = self.urlresolvers[app.module, None]
        except KeyError:
            mr = patterns("")
            self.urlpatterns += [RegexURLResolver("^%s/" % app.module, mr,
                                                  namespace=app.module)]
            self.urlresolvers[app.module, None] = mr
        # Install application URL resolver
        try:
            ar = self.urlresolvers[app.module, app.app]
        except KeyError:
            ar = patterns("")
            mr += [RegexURLResolver("^%s/" % app.app, ar, namespace=app.app)]
            self.urlresolvers[app.module, app.app] = ar
        # Register application views
        umap = {}  # url -> [(URL, view)]
        for view in app.get_views():
            if hasattr(view, "url"):
                for u in self.view_urls(view):
                    m = umap.get(u.url, [])
                    m += [(u, view)]
                    umap[u.url] = m
        for url in umap:
            mm = {}
            names = set()
            for u, v in umap[url]:
                for m in u.method:
                    #if m in mm:
                    #    raise ValueError("Overlapping methods for same URL")
                    mm[m] = v
                if hasattr(v, "menu") and v.menu:
                    self.add_to_menu(app, v)
                if u.name:
                    names.add(u.name)
            sv = self.site_view(app, mm)
            ar += [RegexURLPattern(u.url, sv, name=u.name)]
            for n in names:
                self.register_named_view(app.module, app.app, n, sv)
        # Register application-level menu
        if (hasattr(app, "launch_access") and
            hasattr(app, "menu") and app.menu):
            self.add_app_menu(app)

    def add_module_menu(self, m):
        mod_name = __import__(m, {}, {}, ["MODULE_NAME"]).MODULE_NAME
        r = {"title": mod_name, "children": []}
        self.set_menu_id(r, [m])
        self.menu += [r]

    def autodiscover(self):
        """
        Auto-load and initialize all application classes
        """
        for app in [a for a in INSTALLED_APPS if a.startswith("noc.")]:
            m = app.split(".")[1]
            self.add_module_menu(app)
            # Initialize application
            for f in glob.glob("%s/apps/*/views.py" % m):
                d = os.path.split(f)[0]
                # Skip application loading if denoted by DISABLED file
                if os.path.isfile(os.path.join(d, "DISABLED")):
                    continue
                __import__(".".join(["noc"] + f[:-3].split(os.path.sep)),
                           {}, {}, "*")
            continue
            # Try to install dynamic menus
            menu = None
            try:
                menu = __import__(app + ".menu", {}, {}, "DYNAMIC_MENUS")
            except ImportError:
                continue
            if menu:
                self.app_menu[m].submenus += menu.DYNAMIC_MENUS
        self.sort_menu()

    def application_by_class(self, app_class):
        """
        Get application instance
        """
        return self.apps[app_class.get_app_id()]

    rx_namespace = re.compile(r"^[a-z0-9_]+:[a-z0-9_]+:[a-z0-9_]+$",
                              re.IGNORECASE)

    def reverse(self, url, *args, **kwargs):
        """
        Reverse URL.
        Use common django url reversing scheme
        kwargs QUERY handled as query part
        """
        if self.rx_namespace.match(url):
            kw = kwargs.copy()
            query = ""
            if "QUERY" in kw:
                query = "?" + urllib.urlencode(kw["QUERY"])
                del kw["QUERY"]
            return reverse(url, args=args, kwargs=kw) + query
        else:
            return url

    def sort_menu(self):
        """
        Sort application menu
        """
        def sorted_menu(c):
            c = sorted(c, key=lambda x: x["title"])
            for m in c:
                if "children" in m:
                    m["children"] = sorted_menu(m["children"])
            return c

        for m in self.menu:
            m["children"] = sorted_menu(m["children"])

    def set_menu_id(self, item, path):
        menu_id = hashlib.sha1(" | ".join(path)).hexdigest()
        item["id"] = menu_id
        self.menu_index[menu_id] = item


##
## Global application site instance
##
site = Site()
