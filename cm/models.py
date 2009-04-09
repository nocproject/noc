# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.db import models
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings
from noc.sa.profiles import profile_registry
from noc.settings import config
from noc.lib.url import URL
from noc.lib.fileutils import rewrite_when_differ,read_file,is_differ,in_dir
from noc.lib.validators import is_int
from noc.cm.vcs import vcs_registry
import os,datetime,stat,logging,sets,random
from noc.sa.models import Activator,AdministrativeDomain,ObjectGroup,ManagedObject
from noc.main.menu import Menu
from noc.sa.protocols.sae_pb2 import *
from noc.main.search import SearchResult

profile_registry.register_all()
vcs_registry.register_all()

#
OBJECT_TYPES=["config","dns","prefix-list","rpsl"]
OBJECT_TYPE_CHOICES=[(x,x) for x in OBJECT_TYPES]

class ObjectNotify(models.Model):
    class Meta:
        verbose_name="Object Notify"
        verbose_name_plural="Object Notifies"
    type=models.CharField("Type",max_length=16,choices=OBJECT_TYPE_CHOICES)
    administrative_domain=models.ForeignKey(AdministrativeDomain,verbose_name="Administrative Domain",blank=True,null=True)
    group=models.ForeignKey(ObjectGroup,verbose_name="Group",blank=True,null=True)
    emails=models.CharField("Emails",max_length=128)
    notify_immediately=models.BooleanField("Notify Immediately")
    notify_delayed=models.BooleanField("Notify Delayed")
    def __unicode__(self):
        return "(%s,%s,%s,%s)"%(self.type,self.administrative_domain,self.group,self.emails)

#
class Object(models.Model):
    class Meta:
        abstract=True
    repo_path=models.CharField("Repo Path",max_length=128,unique=True)
    #
    last_modified=models.DateTimeField("Last Modified",blank=True,null=True)
    #
    push_every=models.PositiveIntegerField("Push Every (secs)",default=86400,blank=True,null=True)
    next_push=models.DateTimeField("Next Push",blank=True,null=True)
    last_push=models.DateTimeField("Last Push",blank=True,null=True)
    #
    pull_every=models.PositiveIntegerField("Pull Every (secs)",default=86400,blank=True,null=True)
    next_pull=models.DateTimeField("Next Pull",blank=True,null=True)
    last_pull=models.DateTimeField("Last Pull",blank=True,null=True) # Updated by write() method
    
    def __unicode__(self):
        return "%s/%s"%(self.repo_name,self.repo_path)
    
    def _vcs(self):
        return vcs_registry.get(self.repo)
    vcs=property(_vcs)
        
    def save(self,*args,**kwargs):
        if self.repo_path and not in_dir(self.path,self.repo):
            raise Exception("Attempting to write outside of repo")
        mv=None
        if self._get_pk_val():
            old=self.__class__.objects.get(pk=self._get_pk_val())
            if old.repo_path!=self.repo_path:
                mv=(old.repo_path,self.repo_path)
        models.Model.save(self,*args,**kwargs)
        vcs=self.vcs
        if mv is not None and vcs.in_repo(mv[0]):
            vcs.mv(mv[0],mv[1])
        
    def _repo(self):
        return os.path.join(config.get("cm","repo"),self.repo_name)
    repo=property(_repo)

    def _path(self):
        return os.path.join(self.repo,self.repo_path)
    path=property(_path)
    
    #
    # If "data" differs from object's content in the repository
    # Write "data" to file and commit
    #
    def write(self,data):
        path=self.path
        if not in_dir(path,self.repo):
            raise Exception("Attempting to write outside of repo")
        is_new=not os.path.exists(path)
        now=datetime.datetime.now()
        if rewrite_when_differ(self.path,data):
            vcs=self.vcs
            if is_new:
                vcs.add(self.repo_path)
            vcs.commit(self.repo_path)
            self.last_modified=now
            self.on_object_changed()
        self.last_pull=now
        self.save()
    # Returns object's content
    # Or None if no content yet
    def _data(self):
        return read_file(self.path)
    data=property(_data)
    #
    def delete(self):
        if os.path.exists(self.repo_path):
            self.vcs.rm(self.path)
        super(Object,self).delete()

    def view_link(self):
        return "<A HREF='/cm/view/%s/%d/'>View</A>"%(self.repo_name,self.id)
    view_link.short_description="View"
    view_link.allow_tags=True

    def _revisions(self):
        return self.vcs.log(self.repo_path)
    revisions=property(_revisions)
    
    # Finds revision of the object and returns Revision
    def find_revision(self,rev):
        assert is_int(rev)
        for r in self.revisions:
            if r.revision==rev:
                return r
        raise Exception("Not found")
    
    def diff(self,rev1,rev2):
        return self.vcs.diff(self.repo_path,rev1,rev2)
        
    def get_revision(self,rev):
        return self.vcs.get_revision(self.repo_path,rev)
        
    @classmethod
    def get_object_class(self,repo):
        if repo=="config":
            return Config
        elif repo=="dns":
            return DNS
        elif repo=="prefix-list":
            return PrefixList
        elif repo=="rpsl":
            return RPSL
        else:
            raise Exception("Invalid repo '%s'"%repo)
    
    def change_notify_list(self,immediately=False,delayed=False):
        emails=sets.Set()
        for n in ObjectNotify.objects.filter(type=self.repo_name):
            if immediately and not n.notify_immediately:
                continue
            if delayed and not n.notify_delayed:
                continue
            emails.update(n.emails.split())
        return list(emails)
        
    def on_object_changed(self):
        emails=self.change_notify_list(immediately=True)
        if not emails:
            return
        revs=self.revisions
        now=datetime.datetime.now()
        if len(revs)==1:
            subject="NOC: Object '%s' was created"%str(self)
            message="The object %s was created at %s\n"%(str(self),now)
            message+="Object value follows:\n---------------------------\n%s\n-----------------------\n"%self.data
        else:
            subject="NOC: Object changed '%s'"%str(self)
            message="The object %s was changed at %s\n"%(str(self),now)
            message+="Object changes follows:\n---------------------------\n%s\n-----------------------\n"%self.diff(revs[1],revs[0])
        send_mail(subject=subject,message=message,from_email=settings.SERVER_EMAIL,recipient_list=emails,fail_silently=True)
    ##
    ##
    def push(self): pass
    def pull(self): pass
    #
    # Push all objects of the given type
    #
    @classmethod
    def global_push(self): pass
    #
    # Pull all objects of the given type
    #
    @classmethod
    def global_pull(self): pass
    #
    # Permission checks
    #
    def has_access(self,user):
        if user.is_superuser:
            return True
        return False
    ##
    ## Search engine
    ##
    @classmethod
    def search(cls,user,query,limit):
        for o in [o for o in cls.objects.all() if o.repo_path and o.has_access(user)]:
            data=o.data
            if query in o.repo_path: # If repo_path matches
                yield SearchResult(
                    url="/cm/view/%s/%d/"%(o.repo_name,o.id),
                    title="CM: "+unicode(o),
                    text=unicode(o),
                    relevancy=1.0, # No weighted search yes
                    )                
            elif data and query in data: # Dumb substring search in config
                idx=data.index(query)
                idx_s=max(0,idx-100)
                idx_e=min(len(data),idx+len(query)+100)
                text=data[idx_s:idx_e]
                yield SearchResult(
                    url="/cm/view/%s/%d/"%(o.repo_name,o.id),
                    title="CM: "+unicode(o),
                    text=text,
                    relevancy=1.0, # No weighted search yes
                    )
##
## Config
##
class Config(Object):
    class Meta:
        verbose_name="Config"
        verbose_name_plural="Configs"
    managed_object=models.OneToOneField(ManagedObject,verbose_name="Managed Object",unique=True)
    
    repo_name="config"
    def _profile(self):
        return profile_registry[self.profile_name]()
    profile=property(_profile)
    
    def pull(self,sae):
        def pull_callback(result=None,error=None):
            if error:
                if error.code==ERR_OVERLOAD:
                    timeout=config.getint("cm","timeout_overload")
                elif error.code==ERR_DOWN:
                    timeout=config.getint("cm","timeout_down")
                else:
                    timeout=config.getint("cm","timeout_error")
                variation=config.getint("cm","timeout_variation")
                timeout+=random.randint(-timeout/variation,timeout/variation) # Add jitter to avoid blocking by dead task
                self.next_pull=datetime.datetime.now()+datetime.timedelta(seconds=timeout)
                self.save()
                return            
            if self.pull_every:
                self.next_pull=datetime.datetime.now()+datetime.timedelta(seconds=self.pull_every)
                self.save()
            self.write(result)
        sae.script(self.managed_object,"%s.get_config"%self.managed_object.profile_name,pull_callback)
    def scripts_link(self):
        return "<A HREF='/sa/%d/scripts/'>Scripts</A>"%(self.id)
    scripts_link.short_description="Scripts"
    scripts_link.allow_tags=True
    ##
    ## Access control
    ##
    def has_access(self,user):
        return self.managed_object.has_access(user)
        
    @classmethod
    def queryset(cls,user):
        # Idiotic implementation
        ids=[o.id for o in cls.objects.all() if o.has_access(user)]
        return cls.objects.filter(id__in=ids)
    
    def change_notify_list(self,immediately=False,delayed=False):
        emails=sets.Set()
        for n in ObjectNotify.objects.filter(Q(type=self.repo_name)\
                    &(Q(administrative_domain__isnull=True)|Q(administrative_domain=self.managed_object.administrative_domain))\
                    &(Q(group__isnull=True)|Q(group__in=self.managed_object.groups.all))):
            if immediately and not n.notify_immediately:
                continue
            if delayed and not n.notify_delayed:
                continue
            emails.update(n.emails.split())
        return list(emails)

##
## PrefixList
##
class PrefixList(Object):
    class Meta:
        verbose_name="Prefix List"
        verbose_name_plural="Prefix Lists"
    repo_name="prefix-list"
    @classmethod
    def global_pull(cls):
        from noc.peer.builder import build_prefix_lists
        objects={}
        for o in PrefixList.objects.all():
            objects[o.repo_path]=o
        logging.debug("PrefixList.global_pull(): building prefix lists")
        for peering_point,pl_name,pl in build_prefix_lists():
            logging.debug("PrefixList.global_pull(): writing %s/%s (%d lines)"%(peering_point.hostname,pl_name,len(pl.split("\n"))))
            path=os.path.join(peering_point.hostname,pl_name)
            if path in objects:
                o=objects[path]
                del objects[path]
            else:
                o=PrefixList(repo_path=path)
                o.save()
            o.write(pl)
        for o in objects.values():
            o.delete()
##
## DNS
##
class DNS(Object):
    class Meta:
        verbose_name="DNS Object"
        verbose_name_plural="DNS Objects"
    repo_name="dns"
    @classmethod
    def global_pull(cls):
        from noc.dns.models import DNSZone,DNSServer
        
        objects={}
        changed={}
        for o in DNS.objects.exclude(repo_path__endswith="autozones.conf"):
            objects[o.repo_path]=o
        for z in DNSZone.objects.filter(is_auto_generated=True):
            for ns in z.profile.masters.all():
                path=os.path.join(ns.name,z.name)
                if path in objects:
                    o=objects[path]
                    del objects[path]
                else:
                    logging.debug("DNSHandler.global_pull: Creating object %s"%path)
                    o=DNS(repo_path=path)
                    o.save()
                if is_differ(o.path,z.zonedata(ns)):
                    changed[z]=None
        for o in objects.values():
            logging.debug("DNS.global_pull: Deleting object: %s"%o.repo_path)
            o.delete()
        for z in changed:
            logging.debug("DNS.global_pull: Zone %s changed"%z.name)
            z.serial=z.next_serial
            z.save()
            for ns in z.profile.masters.all():
                path=os.path.join(ns.name,z.name)
                o=DNS.objects.get(repo_path=path)
                o.write(z.zonedata(ns))
        for ns in DNSServer.objects.all():
            logging.debug("DNSHandler.global_pull: Includes for %s rebuilded"%ns.name)
            g=ns.generator_class()
            path=os.path.join(ns.name,"autozones.conf")
            try:
                o=DNS.objects.get(repo_path=path)
            except Object.DoesNotExist:
                o=DNS(repo_path=path)
                o.save()
            o.write(g.get_include(ns))
            
    @classmethod
    def global_push(self):
        from noc.dns.models import DNSZone
        nses={}
        for z in DNSZone.objects.filter(is_auto_generated=True):
            for ns in z.profile.masters.all():
                nses[ns.name]=ns
        for ns in nses.values():
            logging.debug("DNSHandler.global_push: provisioning %s"%ns.name)
            ns.provision_zones()
##
## RPSL
##
class RPSL(Object):
    class Meta:
        verbose_name="RPSL Object"
        verbose_name_plural="RPSL Objects"
    repo_name="rpsl"
    @classmethod
    def global_pull(cls):
        def global_pull_class(name,c,name_fun):
            objects={}
            for o in RPSL.objects.filter(repo_path__startswith=name+os.sep):
                objects[o.repo_path]=o
            for a in c.objects.all():
                if not a.rpsl:
                    continue
                path=os.path.join(name,name_fun(a))
                if path in objects:
                    o=objects[path]
                    del objects[path]
                else:
                    o=RPSL(repo_path=path)
                    o.save()
                o.write(a.rpsl)
            for o in objects.values():
                o.delete()
        from noc.peer.models import AS,ASSet,PeeringPoint
        from noc.dns.models import DNSZone
        logging.debug("RPSL.global_pull(): building RPSL")
        global_pull_class("inet-rtr",PeeringPoint,lambda a:a.hostname)
        global_pull_class("as",AS,lambda a:"AS%d"%a.asn)
        global_pull_class("as-set",ASSet,lambda a:a.name)
        global_pull_class("domain",DNSZone, lambda a:a.name)
    
    @classmethod
    def global_push(cls): pass
##
## Application Menu
##
class AppMenu(Menu):
    app="cm"
    title="Configuration Management"
    items=[
        ("Config",      "/admin/cm/config/",     "cm.change_config"),
        ("DNS Objects", "/admin/cm/dns/",        "cm.change_dns"),
        ("Prefix Lists","/admin/cm/prefixlist/", "cm.change_prefixlist"),
        ("RPSL Objects","/admin/cm/rpsl/",       "cm.change_rpsl"),
        ("Setup",[
            ("Object Notifies","/admin/cm/objectnotify/", "cm.change_objectnotify"),
        ])
    ]
