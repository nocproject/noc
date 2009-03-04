# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
import datetime,random,cPickle,time
from noc.sa.profiles import profile_registry
from noc.sa.periodic import periodic_registry
from noc.sa.script import script_registry
from noc.sa.protocols.sae_pb2 import TELNET,SSH,HTTP
from noc.main.menu import Menu

profile_registry.register_all()
periodic_registry.register_all()
script_registry.register_all()

##
##
##
class AdministrativeDomain(models.Model):
    class Meta:
        verbose_name="Administrative Domain"
        verbose_name_plural="Administrative Domains"
    name=models.CharField("Name",max_length=32,unique=True)
    description=models.TextField("Description",null=True,blank=True)
    def __unicode__(self):
        return self.name
##
##
##
class ObjectGroup(models.Model):
    class Meta:
        verbose_name="Object Group"
        verbose_name_plural="Object Groups"
    name=models.CharField("Name",max_length=32,unique=True)
    description=models.TextField("Description",null=True,blank=True)
    def __unicode__(self):
        return self.name
##
##
##
class Activator(models.Model):
    class Meta:
        verbose_name="Activator"
        verbose_name_plural="Activators"
    name=models.CharField("Name",max_length=32,unique=True)
    ip=models.IPAddressField("IP")
    auth=models.CharField("Auth String",max_length=64)
    is_active=models.BooleanField("Is Active",default=True)
    def __unicode__(self):
        return self.name
##
##
##
class ManagedObject(models.Model):
    class Meta:
        verbose_name="Managed Object"
        verbose_name_plural="Managed Objects"
    name=models.CharField("Name",max_length=64,unique=True)
    is_managed=models.BooleanField("Is Managed?",default=True)
    administrative_domain=models.ForeignKey(AdministrativeDomain,verbose_name="AdministrativeDomain")
    activator=models.ForeignKey(Activator,verbose_name="Activator")
    profile_name=models.CharField("Profile",max_length=128,choices=profile_registry.choices)
    # Access
    scheme=models.IntegerField("Scheme",choices=[(TELNET,"telnet"),(SSH,"ssh"),(HTTP,"http")])
    address=models.CharField("Address",max_length=64)
    port=models.PositiveIntegerField("Port",blank=True,null=True)
    user=models.CharField("User",max_length=32,blank=True,null=True)
    password=models.CharField("Password",max_length=32,blank=True,null=True)
    super_password=models.CharField("Super Password",max_length=32,blank=True,null=True)
    remote_path=models.CharField("Path",max_length=32,blank=True,null=True)
    trap_source_ip=models.IPAddressField("Trap Source IP",null=True)
    trap_community=models.CharField("Trap Community",blank=True,null=True,max_length=64)
    snmp_ro=models.CharField("RO Community",blank=True,null=True,max_length=64)
    snmp_rw=models.CharField("RW Community",blank=True,null=True,max_length=64)
    # CM
    is_configuration_managed=models.BooleanField("Is Configuration Managed?",default=True)
    repo_path=models.CharField("Repo Path",max_length=128,blank=True,null=True)
    #
    groups=models.ManyToManyField(ObjectGroup,verbose_name="Groups",null=True,blank=True)
    #
    def __unicode__(self):
        return self.name
    def config_link(self):
        try:
            return "<A HREF='/cm/view/config/%d/'>Config</A>"%(self.config.id)
        except:
            return ""
    config_link.short_description="Config"
    config_link.allow_tags=True
    
    def scripts_link(self):
        return "<A HREF='/sa/%d/scripts/'>Scripts</A>"%(self.id)
    scripts_link.short_description="Scripts"
    scripts_link.allow_tags=True
    ##
    ## Access control
    ##
    def has_access(self,user):
        if user.is_superuser:
            return True
        return user.useraccess_set.filter(
                    (Q(administrative_domain__isnull=True)|Q(administrative_domain=self.administrative_domain))\
                    &(Q(group__isnull=True)|Q(group__in=self.groups.all))
                    ).count()>0

    def can_change(self,user,administrative_domain,groups):
        if user.is_superuser:
            return True
        if user.useraccess_set.filter(
                (Q(administrative_domain__isnull=True)|Q(administrative_domain=self.administrative_domain))\
                &Q(group__isnull=True)
                ).count()>0:
            return True
        if groups:
            for g in groups:
                if user.useraccess_set.filter(
                        (Q(administrative_domain__isnull=True)|Q(administrative_domain__isnull=self.administrative_domain))\
                        &Q(group=g)
                        ).count()==0:
                    return False
            return True
        return False
        
    @classmethod
    def queryset(cls,user):
        # Idiotic implementation
        ids=[o.id for o in cls.objects.all() if o.has_access(user)]
        return cls.objects.filter(id__in=ids)
    
    def save(self):
        super(ManagedObject,self).save()
        try:
            config=self.config
        except:
            config=None
        if config is None:
            from noc.cm.models import Config
            config=Config(managed_object=self,repo_path=self.repo_path,pull_every=86400)
            config.save()
    
    def delete(self):
        try:
            config=self.config
        except:
            config=None
        if config:
            config.delete()
        super(ManagedObject,self).delete()

##
##
##
class UserAccess(models.Model):
    class Meta:
        verbose_name="User Access"
        verbose_name_plural="User Access"
    user=models.ForeignKey(User,verbose_name="User")
    administrative_domain=models.ForeignKey(AdministrativeDomain,verbose_name="Administrative Domain",blank=True,null=True)
    group=models.ForeignKey(ObjectGroup,verbose_name="Group",blank=True,null=True)
    def __unicode__(self):
        def q(o):
            if o:
                return o.name
            else:
                return "*"
        return "(%s,%s,%s)"%(self.user.username,q(self.administrative_domain),q(self.group))
##
##
##
class TaskSchedule(models.Model):
    periodic_name=models.CharField("Periodic Task",max_length=64,choices=periodic_registry.choices)
    is_enabled=models.BooleanField("Enabled?",default=False)
    run_every=models.PositiveIntegerField("Run Every (secs)",default=86400)
    retries=models.PositiveIntegerField("Retries",default=1)
    retry_delay=models.PositiveIntegerField("Retry Delay (secs)",default=60)
    timeout=models.PositiveIntegerField("Timeout (secs)",default=300)
    next_run=models.DateTimeField("Next Run",auto_now_add=True)
    retries_left=models.PositiveIntegerField("Retries Left",default=1)

    def __unicode__(self):
        return self.periodic_name

    def _periodic_class(self):
        return periodic_registry[self.periodic_name]
    periodic_class=property(_periodic_class)

    @classmethod
    def get_pending_tasks(cls,exclude=None):
        if exclude:
            TaskSchedule.objects.filter(next_run__lte=datetime.datetime.now(),is_enabled=True).exclude(id__in=exclude).order_by("-next_run")
        else:
            return TaskSchedule.objects.filter(next_run__lte=datetime.datetime.now(),is_enabled=True).order_by("-next_run")
##
## Application Menu
##
class AppMenu(Menu):
    app="sa"
    title="Service Activation"
    items=[
        ("Managed Objects", "/admin/sa/managedobject/", "sa.change_managedobject"),
        ("Task Schedules",  "/admin/sa/taskschedule/",  "sa.change_taskschedule"),
        ("Setup", [
            ("Activators",             "/admin/sa/activator/"            , "sa.change_activator"),
            ("Administrative Domains", "/admin/sa/administrativedomain/" , "sa.change_administrativedomain"),
            ("Object Groups",          "/admin/sa/objectgroup/"          , "sa.change_objectgroup"),
            ("User Access",            "/admin/sa/useraccess/"           , "sa.change_useraccess"),
        ])
    ]
