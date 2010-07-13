# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Site implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.http import HttpResponseRedirect
from django.utils.http import urlquote
from django.conf.urls.defaults import *
from django.core.urlresolvers import *
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from noc.settings import INSTALLED_APPS
from noc.lib.debug import error_report
import re,types,glob,os,urllib
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
        self.reports=[]  # app_id -> title
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
                #print error_report()
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
    ## Reverse URL.
    ## Use common django url reversing scheme
    ## kwargs QUERY handled as query part
    ##
    rx_namespace=re.compile(r"^[a-z0-9_]+:[a-z0-9_]+:[a-z0-9_]+$",re.IGNORECASE)
    def reverse(self,url,*args,**kwargs):
        if self.rx_namespace.match(url):
            kw=kwargs.copy()
            query=""
            if "QUERY" in kw:
                query="?"+urllib.urlencode(kw["QUERY"])
                del kw["QUERY"]
            return reverse(url,args=args,kwargs=kw)+query
        else:
            return url
##
## Global application site instance
##
site=Site()
