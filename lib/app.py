# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Application classes
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from __future__ import with_statement
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
from django.db import connection
from noc.settings import INSTALLED_APPS,config
from noc.lib.debug import error_report
from noc.lib.access import *
import logging,os,glob,types,re
##
## Setup Context Processor.
## Used via TEMPLATE_CONTEXT_PROCESSORS variable in settings.py
## Adds "setup" variable to context.
## "setup" is a hash of
##      "installation_name"
##
def setup_processor(request):
    return {
        "setup" : {
            "installation_name" : config.get("customization","installation_name"),
            "logo_url"          : config.get("customization","logo_url"),
            "logo_width"        : config.get("customization","logo_width"),
            "logo_height"       : config.get("customization","logo_height"),
        }
    }
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
## ProxyNone
##
class ProxyNode: pass
##
## URL Data Holder
##
class URL(object):
    def __init__(self,url,name=None):
        self.url=url
        self.name=name
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
        self.views=ProxyNode() # Named views proxy
        self.testing_mode=hasattr(settings,"NOC_TEST")
    ##
    ## Returns URLConf
    ##
    def urls(self):
        return self.urlpatterns
    urls=property(urls)
    ##
    ## Register named application view
    ##
    def register_named_view(self,mod_ns,app_ns,name,view):
        if mod_ns and app_ns and name:
            if not hasattr(self.views,mod_ns):
                setattr(self.views,mod_ns,ProxyNode())
            n=getattr(self.views,mod_ns)
            if not hasattr(n,app_ns):
                setattr(n,app_ns,ProxyNode())
            n=getattr(n,app_ns)
            setattr(n,name,view)
    ##
    ## Generator returning view's URL objects
    ##
    def view_urls(self,view):
        if isinstance(view.url,basestring): # view.url is string type
            yield URL(view.url,name=getattr(view,"url_name",None))
        elif isinstance(view.url,URL): # Explicit URL
            yield view.url
        elif isinstance(view.url,types.ListType) or isinstance(view.url,types.TupleType): # List type
            for o in view.url:
                if isinstance(o,basestring): # Given by string
                    yield URL(o)
                elif isinstance(o,URL):
                    yield o
                else:
                    raise Exception("Invalid URL object: %s"%str(o))
        else:
            raise Exception("Invalid URL object: %s"%str(view.url))
    ##
    ## Register application view
    ##
    def register_view(self,app,view):
        # Prepare namespaces
        mod_ns=app.module
        app_ns=app.app
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
        sv=self.site_view(app,view)
        for u in self.view_urls(view):
            ar+=[RegexURLPattern(u.url,sv,name=u.name)]
            # Register named view
            self.register_named_view(mod_ns,app_ns,u.name,view)
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
    ## Curry application with access
    ##
    def site_access(self,app,view):
        return lambda user: view.access.check(app,user)
    ##
    ## Decorator for view
    ##
    def site_view(self,app,view):
        # Render view
        def inner(request,*args,**kwargs):
            if not request.user or not view.access.check(app,request.user):
                return self.login(request)
            return view(request,*args,**kwargs)
        # Render view in testing mode
        def inner_test(request,*args,**kwargs):
            try:
                return inner(request,*args,**kwargs)
            except:
                print error_report()
                raise
        # Return actual handler
        if self.testing_mode:
            return inner_test
        else:
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
        # Initialize application
        app=app_class(self)
        self.apps[app_id]=app
        # Register application views
        for view in app.get_views():
            if hasattr(view,"url"):
                self.register_view(app,view)
    ##
    ## Auto-load all application classes
    ##
    def autodiscover(self):
        for app in [a for a in INSTALLED_APPS if a.startswith("noc.")]:
            n,m=app.split(".")
            for f in glob.glob("%s/apps/*/views.py"%m):
                __import__(".".join(["noc"]+f[:-3].split(os.path.sep)),{},{},"*")
    ##
    ## Return application instance
    ##
    def application_by_class(self,app_class):
        return self.apps[app_class.get_app_id()]
    ##
    ## Reverse URL
    ##
    rx_namespace=re.compile(r"^[a-z0-9_]+:[a-z0-9_]+:[a-z0-9_]+$",re.IGNORECASE)
    def reverse(self,url,*args,**kwargs):
        if self.rx_namespace.match(url):
            return reverse(url,args=args,kwargs=kwargs)
        else:
            return url
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
    title="APPLICATION TITLE"
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
        request.user.message_set.create(message=message)
    ##
    ## Return path to named template
    ##
    def get_template_path(self,template):
        return [
            os.path.join(self.module,"apps",self.app,"templates",template),
            os.path.join(self.module,"templates",template)
        ]
    ##
    ## Render template within context
    ##
    def render(self,request,template,dict={}):
        return render_to_response(self.get_template_path(template),dict,
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
    def render_wait(self,request,subject=None,text=None,url=None,timeout=5):
        return self.site.views.main.message.wait(request,subject=subject,text=text,timeout=timeout,url=url)
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
        for view in self.get_views():
            if isinstance(view.access,HasPerm):
                p.add(view.access.get_permission(self))
        return p
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
        self.title=self.model._meta.verbose_name_plural
        # Set up template paths
        self.admin.change_form_template=self.get_template_path("change_form.html")+["admin/change_form.html"]
        self.admin.change_list_template=self.get_template_path("change_list.html")+["admin/change_list.html"]
        # Set up permissions
        self.admin.has_change_permission=lambda request,obj=None: self.view_changelist.access.check(self,request.user,obj)
        self.admin.has_add_permission=lambda request,obj=None: self.view_add.access.check(self,request.user,obj)
        self.admin.has_delete_permission=lambda request,obj=None: self.view_delete.access.check(self,request.user,obj)
        ## Set up row-based access
        self.admin.queryset=self.queryset
    
    def queryset(self,request):
        if hasattr(self.model,"user_objects"):
            return self.model.user_objects(request.user)
        else:
            return self.model.objects
        
    def get_menu(self):
        return self.menu
    ##
    ## Populate context
    ##
    def get_context(self,extra_context):
        if extra_context is None:
            extra_context={}
        extra_context["app"]=self
        return extra_context
    
    def view_changelist(self,request,extra_context=None):
        return self.admin.changelist_view(request,self.get_context(extra_context))
    view_changelist.url=r"^$"
    view_changelist.url_name="changelist"
    view_changelist.access=HasPerm("change")
    view_changelist.menu=get_menu
    
    def view_add(self,request,form_url="",extra_context=None):
        return self.admin.add_view(request)
    view_add.url=r"^add/$"
    view_add.url_name="add"
    view_add.access=HasPerm("add")
    
    def view_history(self,request,object_id,extra_context=None):
        return self.admin.history_view(request,object_id,extra_context)
    view_history.url=r"^(\d+)/history/$"
    view_history.url_name="history"
    view_history.access=HasPerm("change")
    
    def view_delete(self,request,object_id,extra_context=None):
        return self.admin.delete_view(request,object_id,self.get_context(extra_context))
    view_delete.url=r"^(\d+)/delete/$"
    view_delete.url_name="delete"
    view_delete.access=HasPerm("delete")
    
    def view_change(self,request,object_id,extra_context=None):
        return self.admin.change_view(request,object_id,self.get_context(extra_context))
    view_change.url=r"^(\d+)/$"
    view_change.url_name="change"
    view_change.access=HasPerm("change")
##
## Load all applications
##
site.autodiscover()