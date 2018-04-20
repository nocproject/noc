# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Site implementation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import re
=======
##----------------------------------------------------------------------
## Site implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import types
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import glob
import os
import urllib
import hashlib
import logging
<<<<<<< HEAD
import json
from collections import defaultdict
import operator
# Third-party modules
from django.http import (HttpResponse, HttpResponseNotFound,
                         HttpResponseForbidden, Http404)
from django.conf.urls import patterns
from django.core.urlresolvers import RegexURLResolver, RegexURLPattern, reverse
from django.conf import settings
from django.utils.encoding import smart_str
import six
import ujson
# NOC modules
from noc.config import config
from noc.core.debug import error_report
=======
from collections import defaultdict
## Django modules
from django.http import HttpResponse, HttpResponseNotFound,\
                        HttpResponseForbidden, Http404
from django.conf.urls.defaults import *
from django.core.urlresolvers import *
from django.conf import settings
from django.utils.simplejson.encoder import JSONEncoder
from django.utils.encoding import smart_str
## NOC modules
from noc.settings import INSTALLED_APPS, config
from noc.lib.debug import error_report
from noc.lib.serialize import json_decode
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

logger = logging.getLogger(__name__)


<<<<<<< HEAD
class ProxyNode:
    pass


HTTP_METHODS = {"GET", "POST", "PUT", "DELETE"}
=======
class DynamicMenu(object):
    title = "DYNAMIC MENU"
    icon = "icon_folder"
    glyph = "folder"

    @property
    def items(self):
        """
        Generator yielding (title, app, access)
        """
        raise StopIteration


class ProxyNode:
    pass

HTTP_METHODS = set(["GET", "POST", "PUT", "DELETE"])
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


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
<<<<<<< HEAD
            if isinstance(method, six.string_types):
                method = [method]
            if not isinstance(method, (list, tuple)):
=======
            if isinstance(method, basestring):
                method = [method]
            if type(method) not in (types.ListType, types.TupleType):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
    folder_glyps = {
        "Setup": "wrench noc-edit",
        "Reports": "file-text noc-preview"
    }

    def __init__(self):
        self.apps = {}  # app_id -> app instance
        self.urlpatterns = patterns("")
        # Install admin: namespace
        # for model applications
        self.admin_patterns = patterns("")  # Django 1.4 compatibility
        self.urlpatterns = [RegexURLResolver(
            "^admin/", self.admin_patterns, namespace="admin")]
        self.urlresolvers = {}  # (module,appp) -> RegexURLResolver
        self.menu = []
<<<<<<< HEAD
        self.menu_roots = {}  # app -> menu
        self.reports = []  # app_id -> title
        self.views = ProxyNode()  # Named views proxy
        self.testing_mode = hasattr(settings, "IS_TEST")
        self.log_api_calls = config.logging.log_api_calls
        self.log_sql_statements = config.logging.log_sql_statements
        self.app_contributors = defaultdict(set)
        self.installed_applications = []
=======
        self.menu_index = {}  # id -> menu item
        self.reports = []  # app_id -> title
        self.views = ProxyNode()  # Named views proxy
        self.testing_mode = hasattr(settings, "IS_TEST")
        self.log_api_calls = (config.has_option("main", "log_api_calls") and
                              config.getboolean("main", "log_api_calls"))
        self.log_sql_statements = config.getboolean("main",
                                                    "log_sql_statements")
        self.app_contributors = defaultdict(set)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

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
<<<<<<< HEAD
        if isinstance(view.url, six.string_types):  # view.url is string type
=======
        if isinstance(view.url, basestring):  # view.url is string type
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            yield URL(view.url,
                      name=getattr(view, "url_name", None),
                      method=getattr(view, "method", None))
        elif isinstance(view.url, URL):  # Explicit URL object
            yield view.url
<<<<<<< HEAD
        elif isinstance(view.url, (list, tuple)):  # List type
            for o in view.url:
                if isinstance(o, six.string_types):  # Given by string
=======
        elif (isinstance(view.url, types.ListType) or
              isinstance(view.url, types.TupleType)):  # List type
            for o in view.url:
                if isinstance(o, basestring):  # Given by string
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
            def nq(s):
                """
                Convert var[]=xxxx to var=xxxx
                """
                if s.endswith("[]"):
                    return s[:-2]
                else:
                    return s

            try:
                v = view_map[request.method]
            except KeyError:
                logger.info("No handler for '%s' method", request.method)
                return HttpResponseNotFound("No handler for '%s' method" % request.method)
            if not request.user or not v.access.check(app, request.user):
                return HttpResponseForbidden()
            to_log_api_call = (self.log_api_calls and
                               hasattr(v, "api") and v.api)
<<<<<<< HEAD
            app_logger = v.__self__.logger
            try:
                # Validate requests
                if getattr(v, "validate", False):
=======
            app_logger = v.im_self.logger
            try:
                # Validate requests
                if (hasattr(v, "validate") and v.validate):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    # Additional validation
                    errors = None
                    if isinstance(v.validate, DictParameter):
                        # Validate via NOC interfaces
                        if request.method == "GET":
                            g = dict((nq(k), v[0] if len(v) == 1 else v)
                                     for k, v in request.GET.lists()
                                     if k != "_dc")
                        else:
                            ct = request.META.get("CONTENT_TYPE")
                            if ct and ("text/json" in ct or
                                       "application/json" in ct):
<<<<<<< HEAD
                                try:
                                    g = ujson.loads(request.raw_post_data)
                                except ValueError as e:
                                    logger.error("Unable to decode JSON: %s", e)
                                    errors = "Unable to decode JSON: %s" % e
                            else:
                                g = dict((k, v[0] if len(v) == 1 else v)
                                         for k, v in request.POST.lists())
                        if not errors:
                            try:
                                kwargs.update(v.validate.clean(g))
                            except InterfaceTypeError as e:
                                errors = str(e)
=======
                                g = json_decode(request.raw_post_data)
                            else:
                                g = dict((k, v[0] if len(v) == 1 else v)
                                           for k, v in request.POST.lists())
                        try:
                            kwargs.update(v.validate.clean(g))
                        except InterfaceTypeError, why:
                            errors = str(why)
                    elif issubclass(v.validate, Form):
                        # Validate via django forms
                        f = v.validate(request.GET)  # @todo: Post
                        if f.is_valid():
                            kwargs.update(f.cleaned_data)
                        else:
                            errors = dict([(f, "; ".join(e))
                                           for f, e in f.errors.items()])
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    if errors:
                        #
                        if to_log_api_call:
                            app_logger.error("ERROR: %s", errors)
                        # Return error response
<<<<<<< HEAD
                        ext_format = "__format=ext" in request.META["QUERY_STRING"].split("&")
                        r = json.dumps({
=======
                        ext_format = ("__format=ext"
                                    in request.META["QUERY_STRING"].split("&"))
                        r = JSONEncoder(ensure_ascii=False).encode({
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                            "status": False,
                            "errors": errors
                        })
                        status = 200 if ext_format else 400  # OK or BAD_REQUEST
                        return HttpResponse(r, status=status,
                                            mimetype="text/json; charset=utf-8")
                # Log API call
                if to_log_api_call:
                    a = {}
                    if request.method in ("POST", "PUT"):
                        ct = request.META.get("CONTENT_TYPE")
                        if ct and ("text/json" in ct or
                                   "application/json" in ct):
<<<<<<< HEAD
                            a = json.loads(request.raw_post_data)
=======
                            a = json_decode(request.raw_post_data)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                        else:
                            a = dict((k, v[0] if len(v) == 1 else v)
                                     for k, v in request.POST.lists())
                    elif request.method == "GET":
                        a = dict((k, v[0] if len(v) == 1 else v)
                                 for k, v in request.GET.lists())
                    app_logger.debug("API %s %s %s",
                                     request.method, request.path, a)
                # Call handler
<<<<<<< HEAD
                r = v(request, *args, **kwargs)
=======
                v.__dict__["hits_metric"] += 1
                with v.__dict__["time_metric"].timer():
                    r = v(request, *args, **kwargs)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                # Dump SQL statements
                if self.log_sql_statements:
                    from django.db import connections
                    tsc = 0
                    sc = defaultdict(int)
                    for conn in connections.all():
                        for q in conn.queries:
                            stmt = q["sql"].strip().split(" ", 1)[0].upper()
                            sc[stmt] += 1
                            tsc += 1
                            app_logger.debug("SQL %(sql)s %(time)ss" % q)
<<<<<<< HEAD
                    x = ", ".join("%s: %d" % (k, cv)
                                  for k, cv in sc.iteritems())
                    if x:
                        x = " (%s)" % x
                    app_logger.debug("SQL statements: %d%s" % (tsc, x))
            except PermissionDenied as e:
                return HttpResponseForbidden(e)
            except Http404 as e:
                return HttpResponseNotFound(e)
            except Exception:
=======
                    x = ", ".join(["%s: %d" % (k, v)
                                   for k, v in sc.iteritems()])
                    if x:
                        x = " (%s)" % x
                    app_logger.debug("SQL statements: %d%s" % (tsc, x))
            except PermissionDenied, why:
                return HttpResponseForbidden(why)
            except Http404, why:
                return HttpResponseNotFound(why)
            except:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                # Generate 500
                r = HttpResponse(
                    content=error_report(logger=app_logger),
                    status=500,
                    mimetype="text/plain; charset=utf-8"
                )
            # Serialize response when necessary
            if not isinstance(r, HttpResponse):
                try:
                    r = HttpResponse(
<<<<<<< HEAD
                        json.dumps(r),
                        mimetype="text/json; charset=utf-8"
                    )
                except Exception:
=======
                        JSONEncoder(ensure_ascii=False).encode(r),
                        mimetype="text/json; charset=utf-8"
                    )
                except:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    error_report(logger=app_logger)
                    r = HttpResponse(error_report(), status=500)
            r["Pragma"] = "no-cache"
            r["Cache-Control"] = "no-cache"
            r["Expires"] = "0"
            return r

<<<<<<< HEAD
        from .access import PermissionDenied
        from noc.sa.interfaces.base import DictParameter, InterfaceTypeError
        return inner

    def register_app_menu(self, app, view=None):
        # Get Menu title
        if view:
            menu = view.menu
        else:
            menu = app.menu
        if callable(menu):
            menu = menu(app)
        # Split to parts
        root = self.menu_roots[app.module]
        path = [app.module]
        if isinstance(menu, six.string_types):
            parts = menu.split("|")
        else:
            parts = menu
        parts = [x.strip() for x in parts]
        # Find proper place
        while len(parts) > 1:
            p = parts.pop(0)
            path += [p]
            new_root = [n for n in root["children"] if n["title"] == p]
            if new_root:
                root = new_root[0]
            else:
                r = {
                    "id": self.get_menu_id(path),
                    "title": p,
                    "children": []
                }
                if p in self.folder_glyps:
                    r["iconCls"] = "fa fa-%s" % self.folder_glyps[p]
                root["children"] += [r]
                root = r
        path += parts
        # Create item
        r = {
            "id": self.get_menu_id(path),
            "title": parts[0],
            "app": app,
            "iconCls": "fa fa-%s noc-edit" % app.glyph
        }
        if view:
            r["access"] = self.site_access(app, view)
            app.menu_url = ("/%s/%s/%s" % (
                app.module, app.app,
                view.url[1:])
            ).replace("$", "")
        else:
            r["access"] = lambda user: app.launch_access.check(app, user)
=======
        from access import PermissionDenied
        from django.forms import Form
        from noc.sa.interfaces import DictParameter, InterfaceTypeError
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
                if p in self.folder_glyps:
                    r["iconCls"] = "fa fa-%s" % self.folder_glyps[p]
                self.set_menu_id(r, path)
                root["children"] += [r]
                root = r
        path += parts
        app.menu_url = ("/%s/%s/%s" % (app.module, app.app,
                                       v.url[1:])).replace("$", "")
        r = {
            "title": parts[0],
            "app": app,
            "access": self.site_access(app, v),
            "iconCls": "fa fa-%s noc-edit" % app.glyph
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
                if p in self.folder_glyps:
                    r["iconCls"] = "fa fa-%s" % self.folder_glyps[p]
                self.set_menu_id(r, path)
                root["children"] += [r]
                root = r
        path += parts
        r = {
            "title": parts[0],
            "app": app,
            "access": lambda user: app.launch_access.check(app, user),
            "iconCls": "fa fa-%s noc-edit" % app.glyph
        }
        self.set_menu_id(r, path)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        root["children"] += [r]

    def register(self, app_class):
        """
        Register application class
        Fetch all view_* methods
        And register them
        """
<<<<<<< HEAD
        self.installed_applications += [app_class]

    def register_url_resolver(self, app):
        # Install module URL resolver
        # @todo: Legacy django part?
=======
        # Register application
        app_id = app_class.get_app_id()
        if app_id in self.apps:
            raise Exception("Application %s is already registered" % app_id)
        # Initialize application
        app = app_class(self)
        self.apps[app_id] = app
        # Install module URL resolver
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
        return ar

    def register_views(self, app, ar):
        umap = defaultdict(list)  # url -> [(URL, view)]
        for view in app.get_views():
            if hasattr(view, "url"):
                for u in self.view_urls(view):
                    umap[u.url] += [(u, view)]
=======
        # Register application views
        umap = {}  # url -> [(URL, view)]
        for view in app.get_views():
            if hasattr(view, "url"):
                for u in self.view_urls(view):
                    m = umap.get(u.url, [])
                    m += [(u, view)]
                    umap[u.url] = m
            vn = view.__name__
            if vn.startswith("api_"):
                vn = vn[4:]
            elif vn.startswith("view_"):
                vn = vn[5:]
            view.__dict__["hits_metric"] = app.metrics.add_metric("%s.hits" % vn)
            view.__dict__["time_metric"] = app.metrics.add_metric("%s.time" % vn)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        for url in umap:
            mm = {}
            names = set()
            for u, v in umap[url]:
                for m in u.method:
<<<<<<< HEAD
                    mm[m] = v
                if getattr(v, "menu", None):
                    self.register_app_menu(app, v)
=======
                    #if m in mm:
                    #    raise ValueError("Overlapping methods for same URL")
                    mm[m] = v
                if hasattr(v, "menu") and v.menu:
                    self.add_to_menu(app, v)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                if u.name:
                    names.add(u.name)
            sv = self.site_view(app, mm)
            # Django 1.4 workaround
            u_name = u.name
            if u_name and u_name.startswith("admin:"):
                if "%" in u_name:
                    u_name = u_name % (app.module, app.app)
                url = "^../%s/%s/%s" % (app.module, app.app, u.url[1:])
                self.admin_patterns += [
                    RegexURLPattern(url, sv, name=u_name.split(":", 1)[1])
                ]
                u_name = u_name.rsplit("_", 1)[1]
            ar += [RegexURLPattern(u.url, sv, name=u_name)]
            for n in names:
                self.register_named_view(app.module, app.app, n, sv)
<<<<<<< HEAD

    def install_application(self, app_class):
        """
        Install application class to the router
        :param app_class:
        :return:
        """
        # Register application
        app_id = app_class.get_app_id()
        if app_id in self.apps:
            raise Exception("Application %s is already registered" % app_id)
        # Initialize application
        app = app_class(self)
        self.apps[app_id] = app
        # Install module URL resolver
        ar = self.register_url_resolver(app)
        # Register application views
        self.register_views(app, ar)
        # Register contributors
        for c in self.app_contributors[app.__class__]:
            c.set_app(app)
        # Register application-level menu
        if hasattr(app, "launch_access") and hasattr(app, "menu") and app.menu:
            self.register_app_menu(app)

    def add_module_menu(self, m):
        mn = "noc.services.web.apps.%s" % m[4:]  # Strip noc.
        mod_name = __import__(mn, {}, {}, ["MODULE_NAME"]).MODULE_NAME
        r = {
            "id": self.get_menu_id([m]),
            "title": mod_name,
            "children": []
        }
=======
        # Register application-level menu
        if (hasattr(app, "launch_access") and
            hasattr(app, "menu") and app.menu):
            self.add_app_menu(app)
        # Register contributors
        for c in self.app_contributors[app.__class__]:
            c.set_app(app)

    def add_module_menu(self, m):
        mod_name = __import__(m, {}, {}, ["MODULE_NAME"]).MODULE_NAME
        r = {"title": mod_name, "children": []}
        self.set_menu_id(r, [m])
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        self.menu += [r]
        return r

    def autodiscover(self):
        """
        Auto-load and initialize all application classes
        """
        if self.apps:
            # Do not discover site twice
            return
<<<<<<< HEAD
        # Connect to mongodb
        import noc.lib.nosql # noqa:F401
        self.installed_applications = []
        prefix = "services/web/apps"
        # Load applications
        installed_apps = [x[4:] for x in settings.INSTALLED_APPS if x.startswith("noc.")]
        self.menu_roots = {}
        for app in installed_apps:
            app_path = os.path.join(prefix, app)
            if not os.path.isdir(app_path):
                continue
            logger.debug("Loading %s applications", app)
            self.menu_roots[app] = self.add_module_menu("noc.%s" % app)
            # Initialize application
            for cs in ["custom", ""]:
                for f in glob.glob("%s/*/views.py" % os.path.join(cs, app_path)):
                    d = os.path.split(f)[0]
                    # Skip application loading if denoted by DISABLED file
                    if os.path.isfile(os.path.join(d, "DISABLED")):
                        continue
                    __import__(".".join(["noc"] + f[:-3].split(os.path.sep)),
                               {}, {}, "*")
        # Install applications
        for app_class in self.installed_applications:
            self.install_application(app_class)
        logger.info("%d applications are installed", len(self.installed_applications))
        self.installed_applications = []
=======
        for app in [a for a in INSTALLED_APPS if a.startswith("noc.")]:
            # Import models
            __import__(app + ".models", {}, {}, "*")
            m = app.split(".")[1]
            root = self.add_module_menu(app)
            # Initialize application
            for f in glob.glob("%s/apps/*/views.py" % m):
                d = os.path.split(f)[0]
                # Skip application loading if denoted by DISABLED file
                if os.path.isfile(os.path.join(d, "DISABLED")):
                    continue
                __import__(".".join(["noc"] + f[:-3].split(os.path.sep)),
                           {}, {}, "*")
            # Try to install dynamic menus
            menu = None
            try:
                menu = __import__(app + ".menu", {}, {}, "DYNAMIC_MENUS")
            except ImportError:
                continue
            if menu:
                for d_menu in menu.DYNAMIC_MENUS:
                    # Add dynamic menu folder
                    dm = {
                        "title": d_menu.title,
                        "iconCls": d_menu.icon,
                        "children": []
                    }
                    path = [m, d_menu.title]
                    self.set_menu_id(dm, path)
                    root["children"] += [dm]
                    # Add items
                    for title, app_id, access in d_menu.items:
                        app = self.apps[app_id]
                        r = {
                            "title": title,
                            "app": app,
                            "access": access,
                            "iconCls": app.icon,
                        }
                        self.set_menu_id(r, path + [title])
                        dm["children"] += [r]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Finally, order the menu
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
<<<<<<< HEAD
            c = sorted(c, key=operator.itemgetter("title"))
=======
            c = sorted(c, key=lambda x: x["title"])
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            for m in c:
                if "children" in m:
                    m["children"] = sorted_menu(m["children"])
            return c

        for m in self.menu:
            m["children"] = sorted_menu(m["children"])

<<<<<<< HEAD
    def get_menu_id(self, path):
        return hashlib.sha1(" | ".join(smart_str(p) for p in path)).hexdigest()
=======
    def set_menu_id(self, item, path):
        menu_id = hashlib.sha1(" | ".join(smart_str(path))).hexdigest()
        item["id"] = menu_id
        self.menu_index[menu_id] = item
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def add_contributor(self, cls, contributor):
        self.app_contributors[cls].add(contributor)

<<<<<<< HEAD
    def iter_predefined_reports(self):
        self.autodiscover()
        for app in self.apps:
            pr = getattr(self.apps[app], "predefined_reports", None)
            if pr:
                for pr in self.apps[app].predefined_reports:
                    yield "%s:%s" % (app, pr), self.apps[app].predefined_reports[pr]


#
# Global application site instance
#
=======
##
## Global application site instance
##
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
site = Site()
