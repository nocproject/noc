# ---------------------------------------------------------------------
# Site implementation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import glob
import os
import hashlib
import logging
import types
from collections import defaultdict
import operator
from urllib.parse import urlencode
from typing import List, Dict
from threading import Lock

# Third-party modules
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden, Http404
from django.urls import path, re_path, include, reverse
from django.conf import settings
from django.utils.encoding import smart_str
from django.views.i18n import JavaScriptCatalog
import orjson
import cachetools
from dataclasses import dataclass

# NOC modules
from noc.config import config
from noc.core.debug import error_report
from noc.core.comp import smart_bytes, smart_text
from noc.core.jsonutils import orjson_defaults

logger = logging.getLogger(__name__)


class ProxyNode(object):
    pass


HTTP_METHODS = {"GET", "POST", "PUT", "DELETE"}


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
            if isinstance(method, str):
                method = [method]
            if not isinstance(method, (list, tuple)):
                raise TypeError("Invalid type for 'method'")
            for m in method:
                if m not in HTTP_METHODS:
                    raise ValueError("Invalid method '%s'" % m)
            self.method = set(method)

    def __repr__(self):
        return "<URL %s>" % smart_text(self)

    def __str__(self):
        s = self.url
        if self.name:
            s += ", name='%s'" % self.name
        return s


@dataclass
class AppPermission(object):
    """
    Application permission.

    Arguments:
        module: Module name
        title: Application title
        name: Permission name
    """

    module: str
    title: str
    name: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "module": self.module,
            "title": self.title,
            "name": self.name,
        }


_perms_lock = Lock()


class Site(object):
    """
    Application site. Registers applications, builds menu and
    handling views
    """

    folder_glyps = {"Setup": "wrench noc-edit", "Reports": "file-text noc-preview"}
    JSON_CONTENT_TYPES = {"text/json", "application/json"}
    _perms_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __init__(self):
        self.apps = {}  # app_id -> app instance
        self.urlpatterns = []
        self.menu = []
        self.menu_roots = {}  # app -> menu
        self.reports = []  # app_id -> title
        self.views = ProxyNode()  # Named views proxy
        self.log_api_calls = config.logging.log_api_calls
        self.log_sql_statements = config.logging.log_sql_statements
        self.app_contributors = defaultdict(set)
        self.app_count = 0
        self.pending_applications = []

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

    def site_access(self, app, view):
        """
        Curry application with access
        """

        def wrap(user):
            return view.access.check(app, user)

        return wrap

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
            if not getattr(v.access, "permit", False) and (
                not request.user or not v.access.check(app, request.user)
            ):
                return HttpResponseForbidden()
            to_log_api_call = self.log_api_calls and hasattr(v, "api") and v.api
            app_logger = v.__self__.logger
            try:
                # Validate requests
                if getattr(v, "validate", False):
                    # Additional validation
                    errors = None
                    if isinstance(v.validate, DictParameter):
                        # Validate via NOC interfaces
                        if request.method == "GET":
                            g = {
                                nq(k): v[0] if len(v) == 1 else v
                                for k, v in request.GET.lists()
                                if k != "_dc"
                            }
                        else:
                            if self.is_json(request.META.get("CONTENT_TYPE")):
                                try:
                                    g = orjson.loads(request.body)
                                except ValueError as e:
                                    logger.error("Unable to decode JSON: %s", e)
                                    errors = "Unable to decode JSON: %s" % e
                            else:
                                g = {k: v[0] if len(v) == 1 else v for k, v in request.POST.lists()}
                        if not errors:
                            try:
                                kwargs.update(v.validate.clean(g))
                            except InterfaceTypeError as e:
                                errors = str(e)
                    if errors:
                        #
                        if to_log_api_call:
                            app_logger.error("ERROR: %s", errors)
                        # Return error response
                        ext_format = "__format=ext" in request.META["QUERY_STRING"].split("&")
                        r = orjson.dumps({"status": False, "errors": errors})
                        status = 200 if ext_format else 400  # OK or BAD_REQUEST
                        return HttpResponse(
                            r, status=status, content_type="text/json; charset=utf-8"
                        )
                # Log API call
                if to_log_api_call:
                    a = {}
                    if request.method in ("POST", "PUT"):
                        ct = request.META.get("CONTENT_TYPE")
                        if ct and ("text/json" in ct or "application/json" in ct):
                            a = orjson.loads(request.body)
                        else:
                            a = {k: v[0] if len(v) == 1 else v for k, v in request.POST.lists()}
                    elif request.method == "GET":
                        a = {k: v[0] if len(v) == 1 else v for k, v in request.GET.lists()}
                    app_logger.debug("API %s %s %s", request.method, request.path, a)
                # Call handler
                r = v(request, *args, **kwargs)
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
                    x = ", ".join("%s: %d" % (k, cv) for k, cv in sc.items())
                    if x:
                        x = " (%s)" % x
                    app_logger.debug("SQL statements: %d%s" % (tsc, x))
            except PermissionDenied as e:
                return HttpResponseForbidden(e)
            except Http404 as e:
                return HttpResponseNotFound(e)
            except Exception:
                # Generate 500
                r = HttpResponse(
                    content=error_report(logger=app_logger),
                    status=500,
                    content_type="text/plain; charset=utf-8",
                )
            # Serialize response when necessary
            if not isinstance(r, HttpResponse):
                try:
                    r = HttpResponse(
                        orjson.dumps(
                            r,
                            option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS,
                            default=orjson_defaults,
                        ),
                        content_type="text/json; charset=utf-8",
                    )
                except Exception:
                    error_report(logger=app_logger)
                    r = HttpResponse(error_report(), status=500)
            r["Pragma"] = "no-cache"
            r["Cache-Control"] = "no-cache"
            r["Expires"] = "0"
            return r

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
        if isinstance(menu, str):
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
                r = {"id": self.get_menu_id(path), "title": p, "children": []}
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
            "iconCls": "fa fa-%s noc-edit" % app.glyph,
        }
        if view:
            r["access"] = self.site_access(app, view)
            app.menu_url = ("/%s/%s/%s" % (app.module, app.app, view.url[1:])).replace("$", "")
        else:
            r["access"] = lambda user: app.launch_access.check(app, user)
        root["children"] += [r]

    def setup_router(self):
        """
        Set up all applications urls
        :return:
        """
        # Collect patterns
        patterns = {}  # module -> app -> pattern
        index_view = None
        for app in self.apps.values():
            mod_chain = patterns.get(app.module)
            if not mod_chain:
                mod_chain = {}
                patterns[app.module] = mod_chain
            app_chain = mod_chain.get(app.app)
            if not app_chain:
                app_chain = []
                mod_chain[app.app] = app_chain
            # Group URLs
            app_url_map = defaultdict(list)  # url -> (URL, view)
            for view in app.iter_views():
                if isinstance(view.url, str):
                    if view.url == "/index.html":
                        index_view = view
                        continue
                    view_url = URL(
                        view.url,
                        name=getattr(view, "url_name", None),
                        method=getattr(view, "method", None),
                    )
                elif isinstance(view.url, URL):
                    view_url = view.url
                else:
                    raise ValueError("Invalid URL object: %s" % view.url)
                app_url_map[view_url.url] += [(view_url, view)]
            # Install URLs
            for url in app_url_map:
                method_map = {}
                names = set()
                for view_url, view in app_url_map[url]:
                    for method in view_url.method:
                        method_map[method] = view
                    if view_url.name:
                        names.add(view_url.name)
                    if getattr(view, "menu", None):
                        self.register_app_menu(app, view)
                site_view = self.site_view(app, method_map)
                app_chain += [re_path(url, site_view, name=view_url.name)]
                for name in names:
                    self.register_named_view(app.module, app.app, name, site_view)
        # Generate router info
        self.urlpatterns = []
        for module in sorted(patterns):
            # Collect nested application routes
            mod_includes = []
            for app in sorted(patterns[module]):
                mod_includes += [path("%s/" % app, include((patterns[module][app], app)))]
            # Install module routes
            self.urlpatterns += [path("%s/" % module, include((mod_includes, module)))]
        # Django JS Translation
        # @todo: Remove?
        self.urlpatterns.append(
            path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog")
        )
        # /index.html
        if index_view:
            self.urlpatterns.append(path("index.html", index_view))

    def register(self, app_class):
        """
        Schedule application class to be installed to the router.
        Scheduling is necessary to allow the class decorators to add custom views

        :param app_class:
        :return:
        """
        app_id = app_class.get_app_id()
        if app_id in self.apps:
            raise Exception("Application %s is already registered" % app_id)
        self.pending_applications += [app_class]

    def do_register(self, app_class):
        """
        Actually register class

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
        # Register contributors
        for c in self.app_contributors[app.__class__]:
            c.set_app(app)
        # Register application-level menu
        if hasattr(app, "launch_access") and hasattr(app, "menu") and app.menu:
            self.register_app_menu(app)
        self.app_count += 1

    def add_module_menu(self, m):
        mn = "noc.services.web.apps.%s" % m[4:]  # Strip noc.
        mod_name = __import__(mn, {}, {}, ["MODULE_NAME"]).MODULE_NAME
        r = {"id": self.get_menu_id([m]), "title": mod_name, "children": []}
        self.menu += [r]
        return r

    def setup_reports(self):
        """
        Auto Load Report
        :return:
        """
        from noc.main.models.report import Report
        from .reportapplication import ReportByConfigApplication

        for report in Report.objects.filter():
            if report.hide:
                continue
            app = types.new_class("ReportByConfigApplication", (ReportByConfigApplication,))
            app.report_id = str(report.id)
            self.do_register(app)

    def autodiscover(self):
        """
        Auto-load and initialize all application classes
        """
        if self.apps:
            # Do not discover site twice
            return
        self.app_count = 0
        prefix = os.path.join("services", "web", "apps")
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
            for cs in config.get_customized_paths("", prefer_custom=True):
                if cs:
                    basename = os.path.basename(os.path.dirname(cs))
                else:
                    basename = "noc"
                for f in glob.glob("%s/*/views.py" % os.path.join(cs, app_path)):
                    d = os.path.split(f)[0]
                    # Skip application loading if denoted by DISABLED file
                    if os.path.isfile(os.path.join(d, "DISABLED")):
                        continue
                    # site.register will be called by metaclass, registering views
                    __import__(
                        ".".join(
                            [basename] + f[:-3].split(os.path.sep)[len(cs.split(os.path.sep)) - 1 :]
                        ),
                        {},
                        {},
                        "*",
                    )
        # Register all collected applications
        for app_class in self.pending_applications:
            self.do_register(app_class)
        self.setup_reports()
        self.pending_applications = []
        # Setup router URLs
        self.setup_router()
        # Install applications
        logger.info("%d applications are installed", self.app_count)
        # Finally, order the menu
        self.sort_menu()

    rx_namespace = re.compile(r"^[a-z0-9_]+:[a-z0-9_]+:[a-z0-9_]+$", re.IGNORECASE)

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
                query = "?%s" % urlencode(kw["QUERY"])
                del kw["QUERY"]
            return reverse(url, args=args, kwargs=kw) + query
        return url

    def sort_menu(self):
        """
        Sort application menu
        """

        def sorted_menu(c):
            c = sorted(c, key=operator.itemgetter("title"))
            for m in c:
                if "children" in m:
                    m["children"] = sorted_menu(m["children"])
            return c

        for m in self.menu:
            m["children"] = sorted_menu(m["children"])

    def get_menu_id(self, path):
        return hashlib.sha1(smart_bytes(" | ".join(smart_str(p) for p in path))).hexdigest()

    def add_contributor(self, cls, contributor):
        self.app_contributors[cls].add(contributor)

    def iter_predefined_reports(self):
        self.autodiscover()
        for app in self.apps:
            pr = getattr(self.apps[app], "predefined_reports", None)
            if pr:
                for pr in self.apps[app].predefined_reports:
                    yield "%s:%s" % (app, pr), self.apps[app].predefined_reports[pr]

    @classmethod
    def is_json(cls, content_type: str) -> bool:
        """
        Check if content-type is JSON
        :param content_type:
        :return:
        """
        if content_type in cls.JSON_CONTENT_TYPES:
            return True
        # Complex content-type
        if content_type and ";" in content_type:
            ct, _ = content_type.rsplit(";", 1)
            return ct.strip() in cls.JSON_CONTENT_TYPES
        return False

    @cachetools.cachedmethod(operator.attrgetter("_perms_cache"), lock=lambda _: _perms_lock)
    def get_app_permissions_list(self) -> List[AppPermission]:
        """
        Get AppPermission for all installed apps.
        """
        from noc.aaa.models.permission import Permission

        r = []
        perms = Permission.objects.values_list("name", flat=True)
        apps = list(self.apps)
        for module in [m for m in settings.INSTALLED_APPS if m.startswith("noc.")]:
            mod = module[4:]
            m = __import__(f"noc.services.web.apps.{mod}", {}, {}, "MODULE_NAME")
            module_name = m.MODULE_NAME
            for app in [app for app in apps if app.startswith(mod + ".")]:
                app_perms = sorted([p for p in perms if p.startswith(app.replace(".", ":") + ":")])
                if app_perms:
                    a = self.apps[app]
                    for p in app_perms:
                        r.append(AppPermission(module=module_name, title=str(a.title), name=p))
        return r


# Site singletone
site = Site()
