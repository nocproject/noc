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
import datetime,random,cPickle,time,types
from noc.sa.profiles import profile_registry
from noc.sa.periodic import periodic_registry
from noc.sa.scripts import reduce_script_registry
from noc.sa.script import script_registry
from noc.sa.protocols.sae_pb2 import TELNET,SSH,HTTP
from noc.main.menu import Menu
from noc.main.search import SearchResult
from noc.lib.fields import PickledField,INETField

profile_registry.register_all()
periodic_registry.register_all()
script_registry.register_all()
reduce_script_registry.register_all()
scheme_choices=[(TELNET,"telnet"),(SSH,"ssh"),(HTTP,"http")]
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
    ip=models.IPAddressField("From IP")
    to_ip=models.IPAddressField("To IP")
    auth=models.CharField("Auth String",max_length=64)
    is_active=models.BooleanField("Is Active",default=True)
    def __unicode__(self):
        return self.name
    ##
    ## Returns true if IP can belong to any activator
    ##
    @classmethod
    def check_ip_access(self,ip):
        return Activator.objects.filter(ip__gte=ip,to_ip__lte=ip).count()>0
##
##
##
class ManagedObject(models.Model):
    class Meta:
        verbose_name="Managed Object"
        verbose_name_plural="Managed Objects"
    name=models.CharField("Name",max_length=64,unique=True)
    is_managed=models.BooleanField("Is Managed?",default=True)
    administrative_domain=models.ForeignKey(AdministrativeDomain,verbose_name="Administrative Domain")
    activator=models.ForeignKey(Activator,verbose_name="Activator")
    profile_name=models.CharField("Profile",max_length=128,choices=profile_registry.choices)
    description=models.CharField("Description",max_length=256,null=True,blank=True)
    # Access
    scheme=models.IntegerField("Scheme",choices=scheme_choices)
    address=models.CharField("Address",max_length=64)
    port=models.PositiveIntegerField("Port",blank=True,null=True)
    user=models.CharField("User",max_length=32,blank=True,null=True)
    password=models.CharField("Password",max_length=32,blank=True,null=True)
    super_password=models.CharField("Super Password",max_length=32,blank=True,null=True)
    remote_path=models.CharField("Path",max_length=32,blank=True,null=True)
    trap_source_ip=INETField("Trap Source IP",null=True,blank=True,default=None)
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
    # Returns object's profile
    def _profile(self):
        try:
            return self._cached_profile
        except AttributeError:
            self._cached_profile=profile_registry[self.profile_name]()
            return self._cached_profile
    profile=property(_profile)
        
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
    
    def action_links(self):
        try:
            l="<A HREF='/cm/view/config/%d/'>Config</A>"%(self.config.id)
        except:
            l=""
        l+="<br/><A HREF='/sa/%d/scripts/'>Scripts</A>"%(self.id)
        return l
    action_links.short_description="Actions"
    action_links.allow_tags=True
        
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
        if user.is_superuser:
            return cls.objects.all()
        # Build query
        r=[]
        p=[]
        for a in user.useraccess_set.all():
            if a.administrative_domain is None and a.group is None: # Full access
                return cls.objects.all()
            rr=[]
            pp=[]
            if a.administrative_domain:
                rr.append("(sa_managedobject.administrative_domain_id=%s)")
                pp.append(a.administrative_domain.id)
            if a.group:
                rr.append("(sa_managedobject.id IN (SELECT managedobject_id FROM sa_managedobject_groups WHERE objectgroup_id=%s))")
                pp.append(a.group.id)
            if len(rr)==1: # Single clause
                r+=rr
            else: # AND together
                r+=["(%s AND %s)"%(rr[0],rr[1])]
            p+=pp
        if not r: # No access
            return cls.objects.extra(where=["0=1"]) # Return empty queryset
        where=" OR ".join(r)
        return cls.objects.extra(where=[where],params=p)
    ##
    ## Override model's save()
    ## Change related Config object as well
    ##
    def save(self):
        super(ManagedObject,self).save()
        try:
            config=self.config # self.config is OneToOne field created by Config
        except:
            config=None
        if config is None: # No related Config object
            if self.is_configuration_managed: # Object is configuration managed, create related object
                from noc.cm.models import Config
                config=Config(managed_object=self,repo_path=self.repo_path,pull_every=86400)
                config.save()
        else: # Update existing config entry when necessary
            if self.repo_path!=self.config.repo_path: # Repo path changed
                config.repo_path=self.repo_path
            if self.is_configuration_managed and config.pull_every is None: # Device is configuration managed but not on periodic pull
                config.pull_every=86400
            elif not self.is_configuration_managed and config.pull_every: # Reset pull_every for unmanaged devices
                config.pull_every=None
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
    ## Search engine
    ##
    @classmethod
    def search(cls,user,query,limit):
        q=Q(repo_path__icontains=query)|Q(name__icontains=query)|Q(address__icontains=query)|Q(user__icontains=query)|Q(description__icontains=query)
        for o in [o for o in cls.objects.filter(q) if o.has_access(user)]:
            relevancy=1.0
            yield SearchResult(
                url="/admin/sa/managedobject/%d/"%o.id,
                title="SA: "+unicode(o),
                text=unicode(o),
                relevancy=relevancy
            )

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
## Object Selector
##
class ManagedObjectSelector(models.Model):
    class Meta:
        verbose_name="Managed Object Selector"
        verbose_name_plural="Managed Object Selectors"
        ordering=["name"]
    name=models.CharField("Name",max_length=64,unique=True)
    description=models.TextField("Description",blank=True,null=True)
    is_enabled=models.BooleanField("Is Enabled",default=True)
    filter_id=models.IntegerField("Filter by ID",null=True,blank=True)
    filter_name=models.CharField("Filter by Name (REGEXP)",max_length=256,null=True,blank=True)
    filter_profile=models.CharField("Filter by Profile",max_length=64,null=True,blank=True,choices=profile_registry.choices)
    filter_address=models.CharField("Filter by Address (REGEXP)",max_length=256,null=True,blank=True)
    filter_administrative_domain=models.ForeignKey(AdministrativeDomain,verbose_name="Filter by Administrative Domain",null=True,blank=True)
    filter_activator=models.ForeignKey(Activator,verbose_name="Filter by Activator",null=True,blank=True)
    filter_user=models.CharField("Filter by User (REGEXP)",max_length=256,null=True,blank=True)
    filter_remote_path=models.CharField("Filter by Remote Path (REGEXP)",max_length=256,null=True,blank=True)
    filter_groups=models.ManyToManyField(ObjectGroup,verbose_name="Filter by Groups",null=True,blank=True)
    filter_description=models.CharField("Filter by Description (REGEXP)",max_length=256,null=True,blank=True)
    filter_repo_path=models.CharField("Filter by Repo Path (REGEXP)",max_length=256,null=True,blank=True)
    source_combine_method=models.CharField("Source Combine Method",max_length=1,default="O",choices=[("A","AND"),("O","OR")])
    sources=models.ManyToManyField("ManagedObjectSelector",verbose_name="Sources",symmetrical=False,null=True,blank=True)
    
    def __unicode__(self):
        return self.name
    ##
    ## Returns a queryset containing selected managed objects
    ##
    def _managed_objects(self):
        # Apply restrictions
        q=Q(is_managed=True)
        if self.filter_id:
            q&=Q(id=self.filter_id)
        if self.filter_name:
            q&=Q(name__regex=self.filter_name)
        if self.filter_profile:
            q&=Q(profile_name=self.filter_profile)
        if self.filter_address:
            q&=Q(address__regex=self.filter_address)
        if self.filter_administrative_domain:
            q&=Q(administrative_domain=self.filter_administrative_domain)
        if self.filter_activator:
            q&=Q(activator=self.filter_activator)
        if self.filter_user:
            q&=Q(user__regex=self.filter_user)
        if self.filter_remote_path:
            q&=Q(remote_path__regex=self.filter_remote_path)
        if self.filter_description:
            q&=Q(description__regex=self.filter_description)
        if self.filter_repo_path:
            q&=Q(repo_path__regex=self.filter_repo_path)
        r=ManagedObject.objects.filter(q)
        # Restrict to groups when necessary
        for g in self.filter_groups.all():
            r=r.extra(where=["id IN (SELECT managedobject_id FROM sa_managedobject_groups WHERE objectgroup_id=%s)"],
                params=[g.id])
        # Restrict to sources
        if self.sources.count():
            sm=self.source_combine_method
            for s in self.sources.all():
                if s.id==self.id: # Do not include self
                    continue
                if sm=="A": # AND
                    r&=s.managed_objects
                else: # OR
                    r|=s.managed_objects
        return r.exclude(profile_name="NOC")
    managed_objects=property(_managed_objects)
    ##
    ## Check Managed Object matches selector
    ##
    def match(self,managed_object):
        return self.managed_objects.filter(id=managed_object.id).count()>0
##
## Reduce Tasks
##
class ReduceTask(models.Model):
    class Meta:
        verbose_name="Map/Reduce Task"
        verbose_name_plural="Map/Reduce Tasks"
    start_time=models.DateTimeField("Start Time")
    stop_time=models.DateTimeField("Stop Time")
    reduce_script=models.CharField("Script",max_length=256,choices=reduce_script_registry.choices)
    script_params=PickledField("Params",null=True,blank=True)
    
    def __unicode__(self):
        if self.id:
            return u"%d: %s"%(self.id,self.reduce_script)
        else:
            return u"New: %s"%(self.reduce_script)
    ##
    ## Check all map tasks are completed
    ##
    def _complete(self):
        return self.stop_time<=datetime.datetime.now()\
            or (self.maptask_set.all().count()==self.maptask_set.filter(status__in=["C","F"]).count())
    complete=property(_complete)
    ##
    ## Create map/reduce tasks
    ##
    @classmethod
    def create_task(self,object_selector,reduce_script,reduce_script_params,map_script,map_script_params,timeout):
        start_time=datetime.datetime.now()
        r_task=ReduceTask(
            start_time=start_time,
            stop_time=start_time+datetime.timedelta(seconds=timeout),
            reduce_script=reduce_script,
            script_params=reduce_script_params,
        )
        r_task.save()
        prepend_profile=len(map_script.split("."))!=3
        if type(object_selector)==types.ListType:
            objects=object_selector
        else:
            objects=object_selector.managed_objects
        for o in objects:
            # Prepend profile name when necessary
            if prepend_profile:
                ms="%s.%s"%(o.profile_name,map_script)
            else:
                ms=map_script
            #
            status="W"
            # Check script is present
            if not ms.startswith(o.profile_name+".")\
                or map_script not in profile_registry[o.profile_name].scripts:
                    # No such script
                    status="F"
            #
            MapTask(
                task=r_task,
                managed_object=o,
                map_script=ms,
                script_params=map_script_params,
                next_try=start_time,
                status=status
            ).save()
        return r_task
    ##
    ## Perform reduce script and execute result
    ##
    def get_result(self):
        return reduce_script_registry[self.reduce_script].execute(self)
    ##
    ## Wait untill all task complete
    ##
    @classmethod
    def wait_for_tasks(cls,tasks):
        while tasks:
            time.sleep(3)
            rest=[]
            for t in tasks:
                if t.complete:
                    t.get_result() # delete task and trigger reduce task
                else:
                    rest+=[t]
                tasks=rest
##
## Map Tasks
##
class MapTask(models.Model):
    class Meta:
        verbose_name="Map/Reduce Task Data"
        verbose_name="Map/Reduce Task Data"
    task=models.ForeignKey(ReduceTask,verbose_name="Task")
    managed_object=models.ForeignKey(ManagedObject,verbose_name="Managed Object")
    map_script=models.CharField("Script",max_length=256)
    script_params=PickledField("Params",null=True,blank=True)
    next_try=models.DateTimeField("Next Try")
    retries_left=models.IntegerField("Retries Left",default=1)
    status=models.CharField("Status",max_length=1,choices=[("W","Wait"),("R","Running"),("C","Complete"),("F","Failed")],default="W")
    script_result=PickledField("Result",null=True,blank=True)
    def __unicode__(self):
        if self.id:
            return u"%d: %s %s"%(self.id,self.managed_object,self.map_script)
        else:
            return u"New: %s %s"%(self.managed_object,self.map_script)
##
## Application Menu
##
class AppMenu(Menu):
    app="sa"
    title="Service Activation"
    items=[
        ("Managed Objects", "/admin/sa/managedobject/", "sa.change_managedobject"),
        ("Map/Reduce Tasks","/sa/mr_task/",             "sa.add_reducetask"),
        ("Task Schedules",  "/admin/sa/taskschedule/",  "sa.change_taskschedule"),
        ("Setup", [
            ("Activators",             "/admin/sa/activator/"            , "sa.change_activator"),
            ("Administrative Domains", "/admin/sa/administrativedomain/" , "sa.change_administrativedomain"),
            ("Object Groups",          "/admin/sa/objectgroup/"          , "sa.change_objectgroup"),
            ("User Access",            "/admin/sa/useraccess/"           , "sa.change_useraccess"),
            ("Object Selectors",       "/admin/sa/managedobjectselector/", "sa.change_managedobjectselector"),
        ])
    ]
