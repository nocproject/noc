# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Application classes
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseForbidden,HttpResponseNotFound
from django.utils.simplejson.encoder import JSONEncoder
from django.conf.urls.defaults import *
from django.core.urlresolvers import *
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings
from django.utils.http import urlquote
from django.contrib import admin as django_admin
import logging,os,glob
##
## Application menu
## Populated by Site
##
class Menu(object):
    def __init__(self,app,title=None):
        if title:
            self.title=title
        else:
            # Try to fetch title from __init__.py
            try:
                m=__import__("noc.%s"%app,{},{},["MODULE_NAME"])
                self.title=m.MODULE_NAME
            except ImportError:
                self.title=app
        self.app=app
        self.submenus=[]
        self.items=[] # (title,url,access)
    ##
    ## Returns Menu object assotiated with title
    ##
    def get_submenu(self,title):
        for sm in self.submenus:
            if sm.title==title:
                return sm
        sm=Menu(self.app,title)
        self.submenus+=[sm]
        return sm
    ##
    ## Add menu item
    ##
    def add_item(self,title,full_url,access):
        self.items+=[(title,full_url,access)]

##
## Application Site
## Registers applications, build menu and handles views
##
class Site(object):
    def __init__(self):
        self.apps={} # app_id -> app instance
        self.urlpatterns=patterns("")
        self.urlresolvers={} # (module,appp) -> RegexURLResolver
        self.menu=[]
        self.app_menu={} # Module -> menu
    ##
    ## Returns URLConf
    ##
    def urls(self):
        return self.urlpatterns
    urls=property(urls)
    ##
    ## Register application view
    ##
    def register_view(self,app,view):
        # Prepare namespaces
        mod_ns=app.module
        app_ns=app.app
        try:
            url_name=view.url_name
        except AttributeError:
            url_name=None
        # Install module URL resolver
        try:
            mr=self.urlresolvers[app.module,None]
        except KeyError:
            mr=patterns("")
            self.urlpatterns+=[RegexURLResolver("^%s/"%app.module,mr,namespace=mod_ns)]
            self.urlresolvers[app.module,None]=mr
        # Install application URL resolver
        try:
            ar=self.urlresolvers[app.module,app.app]
        except KeyError:
            ar=patterns("")
            mr+=[RegexURLResolver("^%s/"%app.app,ar,namespace=app_ns)]
            self.urlresolvers[app.module,app.app]=ar
        # Install view
        ar+=[RegexURLPattern(view.url,self.site_view(app,view),name=url_name)]
        # Install Menu
        if hasattr(view,"menu"):
            # Construct full url to menu item
            # <!> Dirty hack, skip ^ in url
            full_url="/%s/%s/%s"%(app.module,app.app,view.url[1:])
            if full_url.endswith("$"):
                full_url=full_url[:-1]
                menu=view.menu
                if callable(menu):
                    menu=menu(app)
                if menu:
                    try:
                        mm=self.app_menu[app.module]
                    except KeyError:
                        mm=Menu(app.module)
                        self.menu+=[mm]
                        self.app_menu[app.module]=mm
                    menu_path=menu.split("|")
                    while len(menu_path)>1:
                        mm=mm.get_submenu(menu_path.pop(0).strip())
                    mm.add_item(menu_path[0].strip(),full_url,self.site_access(app,view))
    ##
    ## Redirect to login page
    ##
    def login(self,request):
        return HttpResponseRedirect("%s?%s=%s"%(settings.LOGIN_URL,REDIRECT_FIELD_NAME,urlquote(request.get_full_path())))
    ##
    ## Decorator for view.access
    ##
    def site_access(self,app,view):
        def inner(request):
            return view.access(app,request)
        return inner
    ##
    ## Decorator for view
    ##
    def site_view(self,app,view):
        def inner(request,*args,**kwargs):
            if not view.access(app,request):
                return self.login(request)
            return view(request,*args,**kwargs)
        return inner
    ##
    ## Register application class
    ## Fetche all view_* methods
    ## And register them
    ##
    def register(self,app_class):
        # Register application
        app_id=app_class.get_app_id()
        if app_id in self.apps:
            raise Exception("Application %s is already registered"%app_id)
        app=app_class(self)
        self.apps[app_id]=app
        # Register application views
        for n in [n for n in dir(app_class) if n.startswith("view_")]:
            view=getattr(app,n)
            if hasattr(view,"url"):
                self.register_view(app,view)
    ##
    ## Auto-load all application classes
    ##
    def autodiscover(self):
        for f in glob.glob("*/apps/*/views.py"):
            __import__(".".join(["noc"]+f[:-3].split(os.path.sep)),{},{},"*")
##
## Global application site instance
##
site=Site()
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
    ##
    def __init__(self,site):
        self.site=site
        parts=self.__class__.__module__.split(".")
        self.module=parts[1]
        self.app=parts[3]
        self.app_id="%s.%s"%(self.module,self.app)
    ##
    ## Return application id
    ##
    @classmethod
    def get_app_id(cls):
        parts=cls.__module__.split(".")
        return "%s.%s"%(parts[1],parts[3])
    ##
    ## Return path to named template
    ##
    def get_template_path(self,template):
        return os.path.join(self.module,"apps",self.app,"templates",template)
    ##
    ## Render template within context
    ##
    def render(self,request,template,dict={}):
        return render_to_response(self.get_template_path(template),dict,context_instance=RequestContext(request))
    ##
    ## Create plain text response
    ##
    def render_plain_text(self,text):
        return HttpResponse(text,mimetype="text/plain")
    ##
    ## Create serialized JSON-encoded response
    ##
    def render_json(self,obj):
        return HttpResponse(JSONEncoder(ensure_ascii=False).encode(obj),mimetype="text/json")
    ##
    ## Render "success" page
    ##
    def render_success(self,request,subject=None,text=None):
        return self.render(request,"main/success.html",{"subject":subject,"text":text})
    ##
    ## Render "failure" page
    ##
    def render_failure(self,request,subject=None,text=None):
        return self.render(request,"main/failure.html",{"subject":subject,"text":text})
    ##
    ## Render wait page
    ##
    def render_wait(self,request,subject=None,text=None,url=None,timeout=5):
        if url is None:
            url=request.path
        return self.render(request,"main/wait.html",{"subject":subject,"text":text,"timeout":timeout,"url":url})
    ##
    ## Redirect to URL
    ##
    def response_redirect(self,url):
        return HttpResponseRedirect(url)
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
    ## ACL helpers. Must be attached to
    ## view_*.access=
    ##
    
    ## Permit
    def permit(self,request):
        return True
    ## Deny
    def deny(self,request):
        return False
    ## Permit any logged user
    def permit_logged(self,request):
        return request.user and request.user.is_authenticated()
    ## Permit superuser
    def permit_superuser(self,request):
        return request.user and request.user.is_superuser
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
## Django's Model Admin Application Wrapper
##
from django.contrib import admin
class ModelApplication(Application):
    model=None         # subclass of Model
    model_admin = None # subclass of ModelAdmin
    menu = None        # Menu Title
    
    def __init__(self,site):
        super(ModelApplication,self).__init__(site)
        self.admin=self.model_admin(self.model, django_admin.site)
        self.admin.app=self
    ##
    def permit_add(self,request):
        return self.admin.has_add_permission(request)
        
    def permit_change(self,request):
        return self.admin.has_change_permission(request)
        
    def permit_delete(self,request):
        return self.admin.has_delete_permission(request)

    def get_menu(self):
        return self.menu
        
    def view_changelist(self,request,extra_content=None):
        return self.admin.changelist_view(request,extra_content)
    view_changelist.url=r"^$"
    view_changelist.access=permit_change
    view_changelist.menu=get_menu
    
    def view_add(self,request,form_url="",extra_content=None):
        return self.admin.add_view(request)
    view_add.url=r"^add/$"
    view_add.access=permit_add
    
    def view_history(self,request,object_id,extra_content=None):
        return self.admin.history_view(request,object_id,extra_content)
    view_history.url=r"^(\d+)/history/$"
    view_history.access=permit_change
    
    def view_delete(self,request,object_id,extra_content=None):
        return self.admin.delete_view(request,object_id,extra_content)
    view_delete.url=r"^(\d+)/delete/$"
    view_delete.access=permit_delete
    
    def view_change(self,request,object_id,extra_content=None):
        return self.admin.change_view(request,object_id,extra_content)
    view_change.url=r"^(\d+)/$"
    view_change.access=permit_change
    
##
## Load all applications
##
site.autodiscover()