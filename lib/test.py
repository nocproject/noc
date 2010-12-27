# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC Test Suite
##----------------------------------------------------------------------
## Credits: Some ideas are borrowed from django_webtest
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from __future__ import with_statement
from django.test import TestCase
from django.conf import settings
from django.http import HttpResponseServerError
from django.core.handlers.wsgi import WSGIHandler
from django.core.servers.basehttp import AdminMediaHandler
from django.db import close_connection
from django.core import signals,serializers
from noc.lib.app import Application,site
from webtest import TestApp
import unittest
import os,types,re
##
## Prevent closing database connection after each request
##
class WSGIWrapper(object):
    def __init__(self,app):
        self.app=app
    
    def __call__(self, environ, start_response):
        signals.request_finished.disconnect(close_connection)
        try:
            return self.app(environ, start_response)
        finally:
            signals.request_finished.connect(close_connection)
##
## Display traceback instead of 500 error
##
class WSGIExceptionHandler(WSGIHandler):
    def handle_uncaught_exception(self,request,resolver,exc_info):
        return HttpResponseServerError(self._get_traceback(exc_info))
##
## WebTest application wrapper
## Add optional "user" keyword argument
##
class NOCTestApp(TestApp):
    def __init__(self, extra_environ=None, relative_to=None):
        app = WSGIWrapper(AdminMediaHandler(WSGIExceptionHandler()))
        super(NOCTestApp,self).__init__(app,extra_environ,relative_to)
    ##
    ## Pass optional "user" argument to REMOTE_USER
    ##
    def _auth_method(self,method,url,**kwargs):
        if "user" in kwargs:
            extra_environ=kwargs.get("extra_environ",{})
            extra_environ["REMOTE_USER"]=kwargs["user"]
            kwargs["extra_environ"]=extra_environ
            del kwargs["user"]
        return method(url,**kwargs)
    ##
    ## GET method
    ##
    def get(self,url,**kwargs):
        return self._auth_method(super(NOCTestApp,self).get,url,**kwargs)
    ##
    ## POST method
    ##
    def post(self,url,**kwargs):
        return self._auth_method(super(NOCTestApp,self).post,url,**kwargs)
    ##
    ## PUT method
    ##
    def put(self,url,**kwargs):
        return self._auth_method(super(NOCTestApp,self).put,url,**kwargs)
    ##
    ## Delete method
    ##
    def delete(self,url,**kwargs):
        return self._auth_method(super(NOCTestApp,self).delete,url,**kwargs)

##
## NOC Test Case
##
class NOCTestCase(TestCase):
    fixtures=[] # A list of texture files
    def __init__(self,methodName="runTest"):
        super(NOCTestCase,self).__init__(methodName)
        p=self.__class__.__module__.split(".")
        self.test_dir=None
        if p[0]=="noc":
            self.test_dir=os.path.sep.join(p[1:-1])
    ##
    ##
    ##
    def __call__(self,result=None):
        # Patch settings
        MIDDLEWARE_CLASSES=settings.MIDDLEWARE_CLASSES[:]
        AUTHENTICATION_BACKENDS=settings.AUTHENTICATION_BACKENDS[:]
        RemoteUserMiddleware="django.contrib.auth.middleware.RemoteUserMiddleware"
        TLSMiddleware="noc.lib.middleware.TLSMiddleware"
        if RemoteUserMiddleware not in settings.MIDDLEWARE_CLASSES:
            # Install RemoteUserMiddleware before 'noc.main.middleware.TLSMiddleware'
            settings.MIDDLEWARE_CLASSES=list(settings.MIDDLEWARE_CLASSES)
            idx=settings.MIDDLEWARE_CLASSES.index(TLSMiddleware)
            settings.MIDDLEWARE_CLASSES.insert(idx,RemoteUserMiddleware)
        auth_backends = list(settings.AUTHENTICATION_BACKENDS)
        try:
            index=auth_backends.index('django.contrib.auth.backends.ModelBackend')
            auth_backends[index]='django.contrib.auth.backends.RemoteUserBackend'
        except ValueError:
            auth_backends.append('django.contrib.auth.backends.RemoteUserBackend')
        settings.AUTHENTICATION_BACKENDS=auth_backends
        # Init self._app
        self.app=NOCTestApp()
        # Call actual test
        res=super(NOCTestCase,self).__call__(result)
        # Unpatch settings
        settings.MIDDLEWARE_CLASSES=MIDDLEWARE_CLASSES
        settings.AUTHENTICATION_BACKENDS=AUTHENTICATION_BACKENDS
    ##
    ## load fixture
    ##
    def load_fixture(self,file):
        with open(os.path.join(self.test_dir,file)) as f:
            data=f.read()
        for o in serializers.deserialize("json",data):
            o.save()
    ##
    ## Prepare tests and load fixtures
    ##
    def setUp(self):
        super(NOCTestCase,self).setUp() # Call test initialization
        # Load fixtures when given
        if self.test_dir and self.fixtures:
            for f in self.fixtures:
                self.load_fixture(f)
    ##
    ## Check object in collection
    ##
    def assertIn(self,obj,collection):
        self.failUnless(obj in collection,"Object '%s' is not in collection"%(repr(obj)))
    ##
    ## Check object not in collection
    ##
    def assertNotIn(self,obj,collection):
        self.failUnless(obj not in collection,"Object '%s' is in collection"%(repr(obj)))
##
## Model Test Case
##
class ModelTestCase(NOCTestCase):
    model=None
    def __init__(self, methodName='runTest'):
        parts=self.__class__.__module__.split(".")
        super(ModelTestCase,self).__init__(methodName)
    ##
    ## Iterator returning a list of {field:value}
    ##
    def get_data(self):
        return []
    ##
    ##
    ##
    def object_test(self,obj):
        pass
    ##
    ## Test object creation and manipulation
    ##
    def test_object_operations(self):
        data=self.get_data()
        if not data:
            return
        # Find unique fields
        unique_field=None
        for field in self.model._meta.fields:
            if field.unique and field.name!="id":
                unique_field=field.attname
                break
        # Find nullable fields
        null_fields=[f.attname for f in self.model._meta.fields if f.null]
        # Find related fields
        rel_fields=dict([(f.attname,f.rel.to) for f in self.model._meta.fields if f.rel])
        
        unicodes=set()
        # Perform test loop
        for rd in data:
            # Resolve related objects
            for n in rd:
                if n in rel_fields:
                    rd[n[:-3]]=rel_fields[n].objects.get(id=rd[n])
                    del rd[n]
            # Create object
            o=self.model(**rd)
            o.save()
            # Test unicode
            u=unicode(o)
            self.assertNotIn(u,unicodes)
            unicodes.add(u)
            # Find object
            if unique_field:
                ou=self.model.objects.get(**{unique_field:rd[unique_field]})
                self.assertEquals(o.id,ou.id)
            # Additional object tests
            self.object_test(o)
            # Reset nullable fields
            if null_fields:
                for f in null_fields:
                    setattr(o,f,None)
                o.save()
            # Delete object
            o.delete()
##
## Application Test Case
##
class ApplicationTestCase(NOCTestCase):
    user="admin"
    password="admin"
    def __init__(self, methodName='runTest'):
        super(ApplicationTestCase,self).__init__(methodName)
        # Try to deduce application class
        parts=self.__class__.__module__.split(".")
        self._application=None
        if "apps" not in parts or "tests" not in parts:
            return
        parts=parts[:-2]
        vm=".".join(parts+["views"])
        m=__import__(vm,{},{},"*")
        for n in dir(m):
            obj=getattr(m,n)
            if isinstance(obj,(type,types.ClassType)) and issubclass(obj,Application) and obj.__module__==vm:
                self._application=site.application_by_class(obj)
        if not self._application:
            raise Exception("Cannot find application for %s"%self.__class__)
        self._url_name_prefix="%s:%s:"%(parts[1],parts[3])
        self.base_url=self._application.base_url
    ##
    ## Generator returning all relative links in contents area
    ##
    def get_links(self,response):
        text=response.body
        c_re=re.compile(r".*?<!-- Content -->(.*?)<!-- END Content -->.*?",re.I|re.S)
        match=c_re.match(text)
        if not match:
            raise StopIteration
        content=match.group(1)
        # Strip scripts
        tag_script=re.compile(r"<script.+?</script>",re.I|re.S)
        while True:
            nc=tag_script.sub("",content)
            if nc==content:
                break
            else:
                content=nc
        tag_a=re.compile(r"<a\s+(.*?)>.*?</a>",re.I|re.S)
        href=re.compile(r"href\s*=\s*(?P<q>['\"])(?P<link>.*?)(?P=q)",re.I|re.S)
        for d in tag_a.finditer(content):
            match=href.search(d.group(1))
            if match:
                link=match.group("link")
                if not link.startswith("http"):
                    yield link
    ##
    ## Return application views
    ##
    def get_views(self):
        for n in dir(self._application):
            if n.startswith("view_"):
                yield getattr(self._application,n)
    ##
    ## Test URLs can be compiled as re
    ##
    def test_urls(self):
        for v in self.get_views():
            # Check url attribute for view
            if not hasattr(v,"url"):
                raise self.failureException, "View without URL: %s"%str(v)
            # Check access attribute for view
            if not hasattr(v,"access"):
                raise self.failureException, "View without access: %s"%str(v)
            # Test URL compilation
            if isinstance(v.url,basestring):
                try:
                    re.compile(v.url)
                except:
                    raise self.failureException, "Cannot compile URL RE '%s' for view: %s"%(v.url,str(v))
    ##
    ## Try to hit application index URL
    ##
    rx_bc=re.compile(r"<!-- Breadcrumbs -->.+?APPLICATION TITLE.+?<!-- END Breadcrumbs -->",re.MULTILINE|re.DOTALL|re.UNICODE)
    def test_index(self):
        iv=None
        for v in self.get_views():
            if v.url=="^$":
                iv=v
                break
        if not iv: # No index
            return
        # Try to hit index page
        page=self.app.get(self.base_url,user=self.user)
        # Check application name is set
        assert not self.rx_bc.search(page.body),"Application title not set"
        # Try to hit all links on index page
        for l in self.get_links(page):
            ref_page=page.goto(l)
##
## ModelApplicationTestCase
##
class ModelApplicationTestCase(ApplicationTestCase): pass
##
##
##
class ReportApplicationTestCase(ApplicationTestCase):
    posts=None # A list of dictionary to check parametrized reports
    def test_report(self):
        for format in self._application.supported_formats():
            page=self.app.get(self._application.site.reverse(self._application.get_app_id().replace(".",":")+":view",format),user=self.user)

    def test_post(self):
        if self.posts:
            for format in self._application.supported_formats():
                for p in self.posts:
                    r=p.copy()
                    page=self.app.post(self._application.site.reverse(self._application.get_app_id().replace(".",":")+":view",format),
                        user=self.user,
                        params=p)
##
##
##
from noc.sa.models import script_registry,profile_registry
from noc.sa.protocols.sae_pb2 import *
import cPickle
class ActivatorStub(object):
    def __init__(self,test):
        self.to_save_output=None
        self.servers=None
        self.factory=None
        self.log_cli_sessions=None
        self.test=test
        self.use_canned_session=True
    
    def on_script_exit(self,script):
        pass
    
    def cli(self,cmd):
        try:
            return self.test.cli[cmd]
        except KeyError:
            raise Exception("Command not found in canned session: %s"%cmd)
    
    def snmp_get(self,oid):
        try:
            return self.test.snmp_get[oid]
        except KeyError:
            raise Exception("SNMP oid not found in canned session: %s"%oid)
    
    def snmp_getnext(self,oid):
        try:
            return self.test.snmp_getnext[oid]
        except KeyError:
            raise Exception("SNMP oid not found in canned session: %s"%oid)
    
    def get_motd(self):
        return self.test.motd
        

class ScriptTestCase(unittest.TestCase):
    script=None
    vendor=None
    platform=None
    version=None
    input={}
    result=None
    motd=""
    cli=None
    snmp_get={}
    snmp_getnext={}
    mock_get_version=False # Emulate get_version_call
    
    def test_script(self):
        p=self.script.split(".")
        profile=profile_registry[".".join(p[:2])]
        # Prepare access profile
        a=AccessProfile()
        a.profile=profile.name
        if self.snmp_get or self.snmp_getnext:
            a.snmp_ro="public"
        # Run script.
        script=script_registry[self.script](profile(),ActivatorStub(self),a,**self.input)
        # Install mock get_version into cache, if necessary
        s=self.script.split(".")
        if self.mock_get_version and s[-1]!="get_version":
            # Install version info into script call cache
            version={"vendor": self.vendor, "platform": self.platform, "version": self.version}
            script.set_cache("%s.%s.get_version"%(s[0],s[1]), {}, version)
        script.run()
        # Parse script result
        if script.result:
            result=cPickle.loads(script.result)
            self.assertEquals(result,self.result)
        else:
            print script.error_traceback
            self.assertEquals(script.error_traceback,None)
