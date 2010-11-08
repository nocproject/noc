# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Application class
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.template import RequestContext
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseForbidden,HttpResponseNotFound
from django.shortcuts import render_to_response
from django.utils.simplejson.encoder import JSONEncoder
from django.db import connection
from django.shortcuts import get_object_or_404
from access import HasPerm
from site import site
from noc.lib.forms import NOCForm
from noc import settings
import logging,os
##
## Metaclass for Application.
## Register application class to site
##
class ApplicationBase(type):
    def __new__(cls,name,bases,attrs):
        global site
        m=type.__new__(cls,name,bases,attrs)
        if "apps" in m.__module__:
            site.register(m)
        return m
##
## Basic application
## Application combined by set of view_* methods
## Each handling requests
##
class Application(object):
    __metaclass__=ApplicationBase
    title="APPLICATION TITLE"
    extra_permissions=[] # List of additional permissions, not related with views
    ##
    Form=NOCForm # Shortcut for form class
    config=settings.config
    ##
    def __init__(self,site):
        self.site=site
        parts=self.__class__.__module__.split(".")
        self.module=parts[1]
        self.app=parts[3]
        self.module_title=__import__("noc.%s"%self.module,{},{},["MODULE_NAME"]).MODULE_NAME
        self.app_id="%s.%s"%(self.module,self.app)
    ##
    ## Return application id
    ##
    @classmethod
    def get_app_id(cls):
        parts=cls.__module__.split(".")
        return "%s.%s"%(parts[1],parts[3])
    ##
    ## Return application's base url
    ##
    def base_url(self):
        return "/%s/%s/"%(self.module,self.app)
    base_url=property(base_url)
    ##
    ## Reverse URL
    ##
    def reverse(self,url,*args,**kwargs):
        return self.site.reverse(url,*args,**kwargs)
    ##
    ## Send a message to user
    ##
    def message_user(self,request,message):
        request.user.message_set.create(message=unicode(message))
    ##
    ## Return path to named template
    ##
    def get_template_path(self,template):
        return [
            os.path.join(self.module,"apps",self.app,"templates",template),
            os.path.join(self.module,"templates",template),
            os.path.join("templates",template)
        ]
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
    def render_json(self,obj):
        return HttpResponse(JSONEncoder(ensure_ascii=False).encode(obj),mimetype="text/json")
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
        for n in [v for v in dir(self) if v.startswith("view_")]:
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
        for e in self.extra_permissions:
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
    ##
    ## View
    ##
    #def view_test(self,request):
    #    return self.render_text("test")
    #view_test.url=r"^test/"
    #view_test.url_name="test"
    #view_test.access=permit
    #view_test.menu="Test"
##
## @view decorator
##
def view(url,access,url_name=None,menu=None):
    def decorate(f):
        f.url=url
        f.url_name=url_name
        f.access=access
        f.menu=menu
        return f
    return decorate
