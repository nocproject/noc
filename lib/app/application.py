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
from noc.lib.serialize import json_encode


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
    ##
    Form = NOCForm # Shortcut for form class
    config = settings.config
    ##
    def __init__(self,site):
        self.site=site
        parts=self.__class__.__module__.split(".")
        self.module=parts[1]
        self.app=parts[3]
        self.module_title=__import__("noc.%s"%self.module,{},{},["MODULE_NAME"]).MODULE_NAME
        self.app_id="%s.%s"%(self.module,self.app)
        self.menu_url = None  # Set by site.autodiscover()

    @property
    def launch_info(self):
        """
        Return desktop launch information
        """
        return {
            "class": "NOC.main.desktop.IFramePanel",
            "title": unicode(self.title),
            "params": {"url": self.menu_url}
        }

    @classmethod
    def get_app_id(cls):
        """
        Returns application id
        """
        parts=cls.__module__.split(".")
        return "%s.%s"%(parts[1],parts[3])

    @property
    def base_url(self):
        """
        Application's base URL
        """
        return "/%s/%s/"%(self.module,self.app)
    ##
    ## Reverse URL
    ##
    def reverse(self,url,*args,**kwargs):
        return self.site.reverse(url,*args,**kwargs)

    ##
    ## Send a message to user
    ##
    def message_user(self, request, message):
        messages.info(request, unicode(message))
    
    ##
    ## Return path to named template
    ##
    def get_template_path(self, template):
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

    ##
    ## Shortcut to get_object_or_404
    ##
    def get_object_or_404(self,*args,**kwargs):
        return get_object_or_404(*args,**kwargs)
    
    ##
    ## Render template within context
    ##
    def render(self,request,template,dict={},**kwargs):
        return render_to_response(self.get_template_path(template),dict if dict else kwargs,
            context_instance=RequestContext(request,dict={"app":self}))

    ##
    ## Render template to string
    ##
    def render_template(self, template, dict={}, **kwargs):
        tp = self.get_template_path(template)
        return loader.render_to_string(tp, dict or kwargs)

    ##
    ## Render arpitrary Content-Type response
    ##
    def render_response(self,data,content_type="text/plain"):
        return HttpResponse(data,content_type=content_type)
    ##
    ## Create plain text response
    ##
    def render_plain_text(self,text,mimetype="text/plain"):
        return HttpResponse(text,mimetype=mimetype)
    ##
    ## Create serialized JSON-encoded response
    ##
    def render_json(self, obj, status=200):
        return HttpResponse(json_encode(obj),
                            mimetype="text/json", status=status)
    ##
    ## Render "success" page
    ##
    def render_success(self,request,subject=None,text=None):
        return self.site.views.main.message.success(request,subject=subject,text=text)
    ##
    ## Render "failure" page
    ##
    def render_failure(self,request,subject=None,text=None):
        return self.site.views.main.message.failure(request,subject=subject,text=text)
    ##
    ## Render wait page
    ##
    def render_wait(self,request,subject=None,text=None,url=None,timeout=5,progress=None):
        return self.site.views.main.message.wait(request,subject=subject,text=text,timeout=timeout,url=url,progress=progress)
    ##
    ## Redirect to URL
    ##
    def response_redirect(self,url,*args,**kwargs):
        return HttpResponseRedirect(self.reverse(url,*args,**kwargs))
    ##
    ## Redirect to referrer
    ##
    def response_redirect_to_referrer(self,request,back_url=None):
        if back_url is None:
            back_url=self.base_url
        return self.response_redirect(request.META.get("HTTP_REFERER",back_url))
    ##
    ## Redirect to object: {{base.url}}/{{object.id}}/
    ##
    def response_redirect_to_object(self,object):
        return self.response_redirect("%s%d/"%(self.base_url,object.id))
    ##
    ## Render Forbidden response
    ##
    def response_forbidden(self,text=None):
        return HttpResponseForbidden(text)
    ##
    ## Render Not Found response
    ##
    def response_not_found(self,text=None):
        return HttpResponseNotFound(text)
    
    ##
    ## Render javescript closing popup window
    ##
    def close_popup(self, request):
        return self.render(request, "close_popup.html")
    
    ##
    ## Escape HTML
    ##
    def html_escape(self, s):
        return escape(s)
    ##
    ## Logging
    ##
    def debug(self,message):
        logging.debug(message)
    ##
    ## Returns cursor
    ##
    def cursor(self):
        return connection.cursor()
    ##
    ## Execute SQL query
    ##
    def execute(self,sql,args=[]):
        cursor=self.cursor()
        cursor.execute(sql,args)
        return cursor.fetchall()
    ##
    ## AJAX lookup wrapper
    ##
    def lookup(self,request,func):
        result=[]
        if request.GET and "q" in request.GET:
            q=request.GET["q"]
            if len(q)>2: # Ignore requests shorter than 3 letters
                result=list(func(q))
        return self.render_plain_text("\n".join(result))
    ##
    ## Ajax lookup wrapper, returns JSON list of hashes
    ##
    def lookup_json(self,request,func,id_field="id",name_field="name"):
        result=[]
        if request.GET and "q" in request.GET:
            q=request.GET["q"]
            for r in func(q):
                result+=[{id_field:r,name_field:r}]
        return self.render_json(result)
        
    ##
    ## Iterator returning application views
    ##
    def get_views(self):
        for n in [v for v in dir(self) if hasattr(getattr(self, v), "url")]:
            yield getattr(self,n)
    ##
    ## Return a set of permissions, used by application
    ##
    def get_permissions(self):
        p=set()
        # View permissions from HasPerm
        for view in self.get_views():
            if isinstance(view.access,HasPerm):
                p.add(view.access.get_permission(self))
        # extra_permissions
        if callable(self.extra_permissions):
            extra = self.extra_permissions()
        else:
            extra = self.extra_permissions
        for e in extra:
            p.add(HasPerm(e).get_permission(self))
        return p
    ##
    ## Return a list of user access entries
    ##
    def user_access_list(self,user):
        return []
    ##
    ## Return a list of group access entries
    ##
    def group_access_list(self,group):
        return []
    ##
    ## Return an URL to change user access
    ##
    def user_access_change_url(self,user):
        return None
    ##
    ## Return an URL to change group access
    ##
    def group_access_change_url(self,group):
        return None

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
        f.validate = validate
        return f
    return decorate
