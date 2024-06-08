# ---------------------------------------------------------------------
# Application class
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import os
import datetime
import functools
from collections import OrderedDict
from typing import TypeVar, Type

# Third-party modules
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseForbidden,
    HttpResponseNotFound,
)
from django.shortcuts import render
from django.db import connection
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from django.template import loader
from django import forms
from django.utils.timezone import get_current_timezone
from django.views.static import serve as serve_static
from django.http import Http404
import orjson
import jinja2

# NOC modules
from noc.core.forms import NOCForm
from noc import settings
from noc.sa.interfaces.base import DictParameter
from noc.core.cache.base import cache
from noc.core.comp import smart_text
from noc.models import is_document
from .access import HasPerm, Permit, Deny
from .site import site

T = TypeVar("T")


def view(url, access, url_name=None, menu=None, method=None, validate=None, api=False):
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
        if isinstance(access, bool):
            f.access = Permit() if access else Deny()
        elif isinstance(access, str):
            f.access = HasPerm(access)
        else:
            f.access = access
        f.menu = menu
        f.method = method
        f.api = api
        if isinstance(validate, dict):
            f.validate = DictParameter(attrs=validate)
        else:
            f.validate = validate
        return f

    return decorate


class FormErrorsContext(object):
    """
    Catch ValueError exception and populate form's _errors fields
    """

    def __init__(self, form):
        self.form = form

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type == ValueError:
            for ve in exc_val:
                for k in ve:
                    v = ve[k]
                    if not isinstance(v, list):
                        v = [v]
                    self.form._errors[k] = self.form.error_class(v)
            return True


class ApplicationBase(type):
    """
    Application metaclass. Registers application class to site
    """

    def __new__(mcs, name, bases, attrs):
        m = type.__new__(mcs, name, bases, attrs)
        for name in attrs:
            m.add_to_class(name, attrs[name])
        if "apps" in m.__module__:
            site.register(m)
        return m


class Application(object, metaclass=ApplicationBase):
    """
    Basic application class.

    Application combined by set of methods, decorated with @view.
    Each method accepts requests and returns reply
    """

    title = "APPLICATION TITLE"
    icon = "icon_application"
    glyph = "file"
    extra_permissions = []  # List of additional permissions, not related with views
    implied_permissions = {}  # permission -> list of implied permissions
    # When existing permission should be split to separate more granular,
    # it must be set in diverged_permissions like
    # new_permission -> old_permission
    diverged_permissions = {}  # permission -> base permission
    link = None  # Open link in another tab instead of application

    Form = NOCForm  # Shortcut for form class
    config = settings.config  # @fixme remove

    app_alias = None  # Django 1.5 application aliases

    TZ = get_current_timezone()

    def __init__(self, site):
        self.site = site
        self.service = None  # Set by web
        parts = self.__class__.__module__.split(".")
        if parts[1] == "custom":
            self.module = parts[5]
            self.app = parts[6]
        else:
            self.module = parts[4]
            self.app = parts[5]
        self.module_title = __import__(
            "noc.services.web.apps.%s" % self.module, {}, {}, ["MODULE_NAME"]
        ).MODULE_NAME
        self.app_id = "%s.%s" % (self.module, self.app)
        self.menu_url = None  # Set by site.autodiscover()
        self.logger = logging.getLogger(self.app_id)
        self.j2_env = None

    @classmethod
    def add_to_class(cls, name, value):
        if hasattr(value, "contribute_to_class"):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

    def set_app(self, app):
        pass

    @classmethod
    def add_view(
        cls,
        name,
        func,
        url,
        access,
        url_name=None,
        menu=None,
        method=None,
        validate=None,
        api=False,
    ):
        # Decorate function to clear attributes
        f = functools.partial(func)
        f.__self__ = func.__self__
        f.__name__ = func.__name__
        # Add to class
        cls.add_to_class(
            name,
            view(
                url=url,
                access=access,
                url_name=url_name,
                menu=menu,
                method=method,
                validate=validate,
                api=api,
            )(f),
        )
        site.add_contributor(cls, func.__self__)

    @property
    def js_app_class(self):
        return "NOC.main.desktop.IFramePanel"

    def get_launch_info(self, request):
        """
        Return desktop launch information
        """
        from noc.aaa.models.permission import Permission

        user = request.user
        # Amount of characters to strip
        lps = len(self.get_app_id()) + 1
        # Get effective user permissions
        user_perms = Permission.get_effective_permissions(user)
        # Leave only application permissions
        # and strip <module>:<app>:
        app_perms = [p[lps:] for p in user_perms & self.get_permissions()]
        return {
            "class": self.js_app_class,
            "title": smart_text(self.title),
            "params": {
                "url": self.menu_url,
                "permissions": app_perms,
                "app_id": self.app_id,
                "link": self.link,
            },
        }

    @classmethod
    def get_app_id(cls):
        """
        Returns application id
        """
        parts = cls.__module__.split(".")
        if parts[1] == "custom":
            return "%s.%s" % (parts[5], parts[6])
        else:
            return "%s.%s" % (parts[4], parts[5])

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
        if "noc_user" in request.COOKIES:
            session_id = request.COOKIES["noc_user"].rsplit("|", 1)[-1]
            key = "msg-%s" % session_id
            cache.set(key, smart_text(orjson.dumps([message])), ttl=30, version=1)

    def get_template_path(self, template):
        """
        Return path to named template
        """
        if isinstance(template, str):
            template = [template]
        r = []
        for t in template:
            r += [
                os.path.join("services", "web", "apps", self.module, self.app, "templates", t),
                os.path.join(self.module, "templates", t),
                os.path.join("templates", t),
            ]
        return r

    @staticmethod
    def get_object_or_404(model: Type[T], *args, **kwargs) -> T:
        """
        Shortcut to get_object_or_404
        """
        if is_document(model):
            # Document
            r = model.objects.filter(**kwargs).first()
            if r:
                return r
            msg = f"No {model} matching given query"
            raise Http404(msg)
        # Django model
        return get_object_or_404(model, *args, **kwargs)

    def get_environment(self):
        """
        Returns jinja2 environment
        :return:
        """
        if not self.j2_env:
            self.j2_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(
                    [
                        os.path.join("services", "web", "apps", self.module, self.app, "templates"),
                        "templates",
                    ]
                )
            )
        return self.j2_env

    def render(self, request, template, dict=None, **kwargs):
        """
        Render template within context
        """
        if template.endswith(".j2"):
            env = self.get_environment()
            tpl = env.get_template(template)
            return HttpResponse(tpl.render(request=request, app=self, **(dict if dict else kwargs)))
        else:
            ctx = {"app": self}
            if dict:
                ctx.update(dict)
            else:
                ctx.update(kwargs)
            return render(request, self.get_template_path(template), ctx)

    def render_template(self, template, dict=None, **kwargs):
        """
        Render template to string
        """
        dict = dict or {}
        tp = self.get_template_path(template)
        return loader.render_to_string(tp, dict or kwargs)

    @staticmethod
    def render_response(data, content_type="text/plain"):
        """
        Render arbitrary Content-Type response
        """
        return HttpResponse(data, content_type=content_type)

    @staticmethod
    def render_plain_text(text, content_type="text/plain"):
        """
        Render plain/text response
        """
        return HttpResponse(text, content_type=content_type)

    @staticmethod
    def render_json(obj, status=200):
        """
        Create serialized JSON-encoded response
        """
        return HttpResponse(
            orjson.dumps(obj, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS),
            content_type="text/json",
            status=status,
        )

    def render_success(self, request, subject=None, text=None):
        """
        Render "success" page
        """
        return self.site.views.main.message.success(request, subject=subject, text=text)

    def render_failure(self, request, subject=None, text=None):
        """
        Render "failure" page
        """
        return self.site.views.main.message.failure(request, subject=subject, text=text)

    def render_wait(self, request, subject=None, text=None, url=None, timeout=5, progress=None):
        """
        Render wait page
        """
        return self.site.views.main.message.wait(
            request, subject=subject, text=text, timeout=timeout, url=url, progress=progress
        )

    def render_static(self, request, path, document_root=None):
        document_root = document_root or self.document_root
        return serve_static(request, path, document_root=document_root)

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
        return self.response_redirect(request.META.get("HTTP_REFERER", back_url))

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

    def debug(self, message):
        self.logger.debug(message)

    def error(self, message):
        self.logger.error(message)

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

    def iter_views(self):
        """
        Iterator returning application views
        """
        for n in (v for v in dir(self) if v != "model" and hasattr(getattr(self, v), "url")):
            yield getattr(self, n)

    def get_permissions(self):
        """
        Return a set of permissions, used by application
        """
        prefix = self.get_app_id().replace(".", ":")
        p = {"%s:launch" % prefix}
        # View permissions from HasPerm
        for view in self.iter_views():
            if isinstance(view.access, HasPerm):
                p.add(view.access.get_permission(self))
        # mrt_config permissions
        for mrt in self.mrt_config:
            c = self.mrt_config[mrt]
            if "access" in c:
                if isinstance(c["access"], HasPerm):
                    p.add(c["access"].get_permission(self))
                elif isinstance(c["access"], str):
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

    def customize_form(self, form, table, search=False):
        """
        Add custom fields to django form class
        """
        from noc.main.models.customfield import CustomField

        fields = []
        for f in CustomField.table_fields(table):
            if f.is_hidden:
                continue
            if f.type == "str":
                if search and f.is_filtered:
                    ff = forms.ChoiceField(
                        required=False, label=f.label, choices=[("", "---")] + f.get_choices()
                    )
                elif f.enum_group:
                    ff = forms.ChoiceField(
                        required=False, label=f.label, choices=[("", "---")] + f.get_enums()
                    )
                else:
                    ml = f.max_length if f.max_length else 256
                    ff = forms.CharField(required=False, label=f.label, max_length=ml)
            elif f.type == "int":
                ff = forms.IntegerField(required=False, label=f.label)
            elif f.type == "bool":
                ff = forms.BooleanField(required=False, label=f.label)
            elif f.type == "date":
                ff = forms.DateField(required=False, label=f.label)
            elif f.type == "datetime":
                ff = forms.DateTimeField(required=False, label=f.label)
            else:
                raise ValueError("Invalid field type: '%s'" % f.type)
            fields += [(str(f.name), ff)]
        form.base_fields.update(OrderedDict(fields))
        return form

    def apply_custom_fields(self, o, v, table):
        """
        Apply custom fields to form
        :param o: Object
        :param v: values dict
        :param table: table
        :return:
        """
        from noc.main.models.customfield import CustomField

        for f in CustomField.table_fields(table):
            n = str(f.name)
            if n in v:
                setattr(o, n, v[n])
        return o

    def apply_custom_initial(self, o, v, table):
        """

        :param o: Object
        :param v: Initial data
        :param table: table
        :return:
        """
        from noc.main.models.customfield import CustomField

        for f in CustomField.table_fields(table):
            n = str(f.name)
            if n not in v:
                x = getattr(o, n)
                if x:
                    v[n] = x
        return o

    def form_errors(self, form):
        """
        with self.form_errors(form):
            object.save()
        :param form:
        :return:
        """
        return FormErrorsContext(form)

    def to_json(self, v):
        """
        Convert custom types to json string
        :param v:
        :return:
        """
        if v is None:
            return None
        elif isinstance(v, datetime.datetime):
            return v.astimezone(self.TZ).isoformat()
        else:
            raise Exception("Invalid to_json type")

    @view(url="^launch_info/$", method=["GET"], access="launch", api=True)
    def api_launch_info(self, request):
        return self.get_launch_info(request)

    # name -> {access: ..., map_script: ..., timeout: ...}
    mrt_config = {}
