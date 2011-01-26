# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python Modules
from __future__ import with_statement
import os
import datetime
import re
import threading
## Django Modules
from django.db import models
from django.contrib.auth.models import User,Group
from django.core.validators import MaxLengthValidator
from django.contrib import databrowse
from django.db.models.signals import class_prepared,pre_save, pre_delete, post_save, post_delete
## NOC Modules
from noc import settings
from noc.lib.fields import BinaryField
from noc.lib.database_storage import DatabaseStorage as DBS
from noc.main.refbooks.downloaders import downloader_registry
from noc.lib.fields import TextArrayField,PickledField,ColorField
from noc.lib.middleware import get_user
from noc.lib.timepattern import TimePattern as TP
from noc.lib.timepattern import TimePatternList
from noc.sa.interfaces.base import interface_registry
from noc.lib.app.site import site
##
## A hash of Model.search classmethods.
## Populated by "class_prepared" signal listener
## Model.search is a generator taking parameters (user,query,limit)
## And yielding a SearchResults (ordered by relevancy)
##
search_methods={}
##
## Register new search handler if model has .search classmethod
##
def on_new_model(sender,**kwargs):
    if hasattr(sender,"search"):
        search_methods[getattr(sender,"search")]=None
    databrowse.site.register(sender)
##
## Attach to the 'class_prepared' signal
## and on_new_model on every new model
##
class_prepared.connect(on_new_model)
##
## Exclude tables from audit
##
AUDIT_TRAIL_EXCLUDE=set([
    "django_admin_log",
    "django_session",
    "auth_message",
    "main_audittrail",
    "kb_kbentryhistory",
    "kb_kbentrypreviewlog",
    "fm_eventlog",
    "sa_maptask",
    "sa_reducetask",
])
##
## Audit trail for INSERT and UPDATE operations
##
def audit_trail_save(sender,instance,**kwargs):
    # Exclude tables
    if sender._meta.db_table in AUDIT_TRAIL_EXCLUDE:
        return
    #
    if instance.id:
        # Update
        try:
            old=sender.objects.get(id=instance.id)
        except sender.DoesNotExist: # Protection for correct test fixtures loading
            return
        message=[]
        operation="M"
        for f in sender._meta.fields:
            od=f.value_to_string(old)
            nd=f.value_to_string(instance)
            if f.name=="id":
                message+=["id: %s"%nd]
            elif nd!=od:
                message+=["%s: '%s' -> '%s'"%(f.name,od,nd)]
        message="\n".join(message)
    else:
        # New record
        operation="C"
        message="\n".join(["%s = %s"%(f.name,f.value_to_string(instance)) for f in sender._meta.fields])
    AuditTrail.log(sender,instance,operation,message)
##
## Audit trail for delete operations
##
def audit_trail_delete(sender,instance,**kwargs):
    # Exclude tables
    if sender._meta.db_table in AUDIT_TRAIL_EXCLUDE:
        return
    #
    operation="D"
    message="\n".join(["%s = %s"%(f.name,f.value_to_string(instance)) for f in sender._meta.fields])
    AuditTrail.log(sender,instance,operation,message)
##
## Set up audit trail handlers
##
if settings.IS_WEB:
    pre_save.connect(audit_trail_save)
    pre_delete.connect(audit_trail_delete)
##
## Initialize download registry
##
downloader_registry.register_all()
##
## Audit Trail
##
class AuditTrail(models.Model):
    class Meta:
        verbose_name="Audit Trail"
        verbose_name_plural="Audit Trail"
        ordering=["timestamp"]
    user=models.ForeignKey(User,verbose_name="User")
    timestamp=models.DateTimeField("Timestamp",auto_now=True)
    model=models.CharField("Model",max_length=128)
    db_table=models.CharField("Table",max_length=128)
    operation=models.CharField("Operation",max_length=1,choices=[("C","Create"),("M","Modify"),("D","Delete")])
    subject=models.CharField("Subject",max_length=256)
    body=models.TextField("Body")
    ##
    ## Log Audit Trail
    ##
    @classmethod
    def log(cls,sender,instance,operation,message):
        user=get_user() # Retrieve user from thread local storage
        if not user or not user.is_authenticated():
            return # No user initialized, no audit trail
        subject=unicode(instance)
        if len(subject)>127:
            # Narrow subject
            subject=subject[:62]+" .. "+subject[-62:]
        AuditTrail(
            user=user,
            model=sender.__name__,
            db_table=sender._meta.db_table,
            operation=operation,
            subject=subject,
            body=message
        ).save()
##
## Permissions
## Populated by manage.py sync-perm
##
class Permission(models.Model):
    class Meta:
        verbose_name="Permission"
        verbose_name_plural="Permissions"
    name=models.CharField("Name",max_length=128,unique=True) # module:app:permission
    users=models.ManyToManyField(User,related_name="noc_user_permissions")
    groups=models.ManyToManyField(Group,related_name="noc_group_permissions")
    def __unicode__(self):
        return self.name
    ##
    ## Checks the user has permission directly or via group
    ##
    @classmethod
    def has_perm(self,user,perm):
        if not user.is_active:
            return False
        if user.is_superuser:
            return True
        p=Permission.objects.get(name=perm)
        return bool(p.users.filter(id=user.id)) or bool(p.groups.filter(id__in=user.groups.all()))
    ##
    ## Return a set of user permissions
    ##
    @classmethod
    def get_user_permissions(cls,user):
        return set(user.noc_user_permissions.values_list("name",flat=True))
    ##
    ## Set user permissions to ``perm``. Perm must be set([])
    ##
    @classmethod
    def set_user_permissions(cls,user,perms):
        current=cls.get_user_permissions(user)
        # Add new permissions
        for p in perms-current:
            Permission.objects.get(name=p).users.add(user)
        # Revoke permissions
        for p in current-perms:
            Permission.objects.get(name=p).users.remove(user)
    ##
    ## Returns a set of group permissions
    ##
    @classmethod
    def get_group_permissions(cls,group):
        return set(group.noc_group_permissions.values_list("name",flat=True))
    ##
    ## Set group permissions
    ##
    @classmethod
    def set_group_permissions(cls,group,perms):
        current=cls.get_group_permissions(group)
        # Add new permissions
        for p in perms-current:
            Permission.objects.get(name=p).groups.add(group)
        # Revoke permissions
        for p in current-perms:
            Permission.objects.get(name=p).groups.remove(group)
    
##
## CSS Styles
##
class Style(models.Model):
    class Meta:
        verbose_name="Style"
        verbose_name_plural="Styles"
    
    name=models.CharField("Name",max_length=64,unique=True)
    font_color=ColorField("Font Color",default=0)
    background_color=ColorField("Background Color",default=0xffffff)
    bold=models.BooleanField("Bold",default=False)
    italic=models.BooleanField("Italic",default=False)
    underlined=models.BooleanField("Underlined",default=False)
    is_active=models.BooleanField("Is Active",default=True)
    description=models.TextField("Description",null=True,blank=True)
    
    def __unicode__(self):
        return self.name
    
    ##
    ## CSS class name
    ##
    @property
    def css_class_name(self):
        return u"noc-color-%d"%self.id
    
    ##
    ##
    ##
    @property
    def style(self):
        s=u"color: %s; background-color: %s;"%(self.font_color,self.background_color)
        if self.bold:
            s+=u" font-weight: bold;"
        if self.italic:
            s+=u" font-style: italic;"
        if self.underlined:
            s+=u" text-decoration: underline;"
        return s
    
    ##
    ## CSS style
    ##
    @property
    def css(self):
        return u".%s { %s }\n"%(self.css_class_name,self.style)
    

##
## Languages
##
class Language(models.Model):
    class Meta:
        verbose_name="Language"
        verbose_name_plural="Languages"
        ordering=("name",)
    name=models.CharField("Name",max_length=32,unique=True)
    native_name=models.CharField("Native Name",max_length=32)
    is_active=models.BooleanField("Is Active",default=False)
    def __unicode__(self):
        return self.name
##
##
##
class DatabaseStorage(models.Model):
    class Meta:
        verbose_name="Database Storage"
        verbose_name_plural="Database Storage"
    name=models.CharField("Name",max_length=256,unique=True)
    data=BinaryField("Data")
    size=models.IntegerField("Size")
    mtime=models.DateTimeField("MTime")
    ##
    ## Options for DatabaseStorage
    ##
    @classmethod
    def dbs_options(cls):
        return {
            "db_table"     : DatabaseStorage._meta.db_table,
            "name_field"  : "name",
            "data_field"  : "data",
            "mtime_field" : "mtime",
            "size_field"  : "size",
        }
    ##
    ## Returns DatabaseStorage instance
    ##
    @classmethod
    def get_dbs(cls):
        return DBS(cls.dbs_options())
##
## Default database storage
##
database_storage=DatabaseStorage.get_dbs()
##
## Extension to MIME-type mapping
##
class MIMEType(models.Model):
    class Meta:
        verbose_name="MIME Type"
        verbose_name_plural="MIME Types"
    extension=models.CharField("Extension",max_length=32,unique=True)
    mime_type=models.CharField("MIME Type",max_length=63)
    def __unicode__(self):
        return u"%s -> %s"%(self.extension,self.mime_type)
    ##
    ## Determine MIME type from filename
    ##
    @classmethod
    def get_mime_type(cls,filename):
        r,ext=os.path.splitext(filename)
        try:
            m=MIMEType.objects.get(extension=ext)
            return m.mime_type
        except MIMEType.DoesNotExist:
            return "application/octet-stream"
##
## pyRule
##
class NoPyRuleException(Exception): pass
rx_coding=re.compile(r"^#\s*-\*-\s*coding:\s*\S+\s*-\*-\s*$",re.MULTILINE)

class PyRule(models.Model):
    class Meta:
        verbose_name="pyRule"
        verbose_name_plural="pyRules"
    name=models.CharField("Name",max_length=64,unique=True)
    interface=models.CharField("Interface",max_length=64,choices=[(i,i) for i in sorted(interface_registry)])
    description=models.TextField("Description")
    text=models.TextField("Text")
    is_builtin=models.BooleanField("Is Builtin",default=False)
    changed=models.DateTimeField("Changed",auto_now=True,auto_now_add=True)
    # Compiled pyRules cache
    compiled_pyrules={}
    compiled_changed={}
    compiled_lock=threading.Lock()
    NoPyRule=NoPyRuleException
    def __unicode__(self):
        return self.name
    # Check syntax
    def save(self,**kwargs):
        self.compile_text(unicode(self.text))
        super(PyRule,self).save(**kwargs)
    # Returns an interface class
    def _interface_class(self):
        return interface_registry[self.interface]
    interface_class=property(_interface_class)
    ##
    @classmethod
    def compile_text(self,text):
        # Built-in pyRule decorator
        def pyrule(f):
            f.is_pyrule=True
            return f
        # Inject @pyrule decorator into namespace
        d={"pyrule":pyrule}
        # Remove coding declarations and \r
        text=rx_coding.sub("",text.replace("\r\n","\n"))
        # Compile text
        exec text in d
        # Find marked pyrule
        rules=[r for r in d.values() if hasattr(r,"is_pyrule") and r.is_pyrule]
        if len(rules)<1:
            raise SyntaxError("No @pyrule decorated symbol found")
        if len(rules)!=1:
            raise SyntaxError("More than one @pyrule deorated symbols found")
        rule=rules[0]
        if not callable(rule):
            raise SyntaxError("Rule is not callable")
        return rule
    ##
    ## Call pyRule
    ##
    def __call__(self,**kwargs):
        t=datetime.datetime.now()
        # Try to get compiled rule from cache
        with self.compiled_lock:
            requires_recompile=self.name not in self.compiled_changed or self.compiled_changed[self.name]<self.changed
            if not requires_recompile:
                f=self.compiled_pyrules[self.name]
        # Recompile rule and place in cache when necessary
        if requires_recompile:
            f=self.compile_text(str(self.text))
            with self.compiled_lock:
                self.compiled_pyrules[self.name]=f
                self.compiled_changed[self.name]=t
        # Check interface
        i=self.interface_class()
        kwargs=i.clean(**kwargs)
        # Evaluate pyRule
        result=f(**kwargs)
        # Check and result
        return i.clean_result(result)
    ##
    ## Call named PyRule
    ##
    @classmethod
    def call(cls,py_rule_name,**kwargs):
        try:
            rule=PyRule.objects.get(name=py_rule_name)
        except PyRule.DoesNotExist:
            raise cls.NoPyRule
        return rule(**kwargs)
##
## Search patters
##
rx_mac_3_octets=re.compile("^([0-9A-F]{6}|[0-9A-F]{12})$",re.IGNORECASE)
##
## Reference Books
##
class RefBook(models.Model):
    class Meta:
        verbose_name="Ref Book"
        verbose_name_plural="Ref Books"
    name=models.CharField("Name",max_length=128,unique=True)
    language=models.ForeignKey(Language,verbose_name="Language")
    description=models.TextField("Description",blank=True,null=True)
    is_enabled=models.BooleanField("Is Enabled",default=False)
    is_builtin=models.BooleanField("Is Builtin",default=False)
    downloader=models.CharField("Downloader",max_length=64,choices=downloader_registry.choices,blank=True,null=True)
    download_url=models.CharField("Download URL",max_length=256,null=True,blank=True)
    last_updated=models.DateTimeField("Last Updated",blank=True,null=True)
    next_update=models.DateTimeField("Next Update",blank=True,null=True)
    refresh_interval=models.IntegerField("Refresh Interval (days)",default=0)
    # Update interval here
    def __unicode__(self):
        return self.name
    ##
    ## Add new record. data is a hash of field name -> value
    ##
    def add_record(self,data):
        fields={}
        for f in self.refbookfield_set.all():
            fields[f.name]=f.order-1
        r=[None for f in range(len(fields))]
        for k,v in data.items():
            r[fields[k]]=v
        RefBookData(ref_book=self,value=r).save()
    ##
    ## Flush entire Ref Book
    ##
    def flush_refbook(self):
        RefBookData.objects.filter(ref_book=self).delete()
    ##
    ## Bulk upload
    ## Data is a list of hashes [{field_name:value,...},...]
    ##
    def bulk_upload(self,data):
        fields={}
        for f in self.refbookfield_set.all():
            fields[f.name]=f.order-1
        row_template=[None for f in range(len(fields))] # Prepare empty row template
        for r in data:
            row=row_template[:] # Clone template row
            for k,v in r.items():
                if k in fields:
                    row[fields[k]]=v
            RefBookData(ref_book=self,value=row).save()
    ##
    ## Download refbook
    ##
    def download(self):
        if self.downloader and self.downloader in downloader_registry.classes:
            downloader=downloader_registry[self.downloader]
            data=downloader.download(self)
            if data:
                self.flush_refbook()
                self.bulk_upload(data)
                self.last_updated=datetime.datetime.now()
                self.next_update=self.last_updated+datetime.timedelta(days=self.refresh_interval)
                self.save()
    ##
    ## Search engine plugin
    ##
    @classmethod
    def search(cls,user,search,limit):
        from noc.lib.search import SearchResult # Must be inside method to prevent import loops
        for b in RefBook.objects.filter(is_enabled=True):
            field_names=[f.name for f in b.refbookfield_set.order_by("order")]
            for f in b.refbookfield_set.filter(search_method__isnull=False):
                x=f.get_extra(search)
                if not x:
                    continue
                q=RefBookData.objects.filter(ref_book=b).extra(**x)
                for r in q:
                    text="\n".join(["%s = %s"%(k,v) for k,v in zip(field_names,r.value)])
                    yield SearchResult(
                        url=("main:refbook:item",b.id,r.id),
                        title=u"Reference Book: %s, column %s"%(b.name,f.name),
                        text=text,
                        relevancy=1.0,
                    )
    ##
    ## Returns true if refbook has at least one searchable field
    ##
    def _can_search(self):
        return self.refbookfield_set.filter(search_method__isnull=False).count()>0
    can_search=property(_can_search)
    ##
    ## Return a fields sorted by order
    ##
    def _fields(self):
        return self.refbookfield_set.order_by("order")
    fields=property(_fields)
##
## Ref Book Fields
##
class RefBookField(models.Model):
    class Meta:
        verbose_name="Ref Book Field"
        verbose_name_plural="Ref Book Fields"
        unique_together=[("ref_book","order"),("ref_book","name")]
        ordering=["ref_book","order"]
    ref_book=models.ForeignKey(RefBook,verbose_name="Ref Book")
    name=models.CharField("Name",max_length="64")
    order=models.IntegerField("Order")
    is_required=models.BooleanField("Is Required",default=True)
    description=models.TextField("Description",blank=True,null=True)
    search_method=models.CharField("Search Method",max_length=64,blank=True,null=True,
        choices=[("string","string"),("substring","substring"),("starting","starting"),("mac_3_octets_upper","3 Octets of the MAC")])
    def __unicode__(self):
        return u"%s: %s"%(self.ref_book,self.name)
    # Return **kwargs for extra
    def get_extra(self,search):
        if self.search_method:
            return getattr(self,"search_%s"%self.search_method)(search)
        else:
            return {}
    # String match
    def search_string(self,search):
        return {
            "where" : ["value[%d] ILIKE %%s"%self.order],
            "params": [search]
        }
    # Substring match
    def search_substring(self,search):
        return {
            "where" : ["value[%d] ILIKE %%s"%self.order],
            "params": ["%"+search+"%"]
        }
    # Starting
    def search_starting(self,search):
        return {
            "where" : ["value[%d] ILIKE %%s"%self.order],
            "params": [search+"%"]
        }
    # Match first 3 octets of the mac address
    def search_mac_3_octets_upper(self,search):
        mac=search.replace(":","").replace("-","").replace(".","")
        if not rx_mac_3_octets.match(mac):
            return {}
        return {
            "where" : ["value[%d]=%%s"%self.order],
            "params": [mac]
        }
##
## Ref Book Data
##
class RBDManader(models.Manager):
    # Order by first field
    def get_query_set(self):
        return super(RBDManader,self).get_query_set().extra(order_by=["main_refbookdata.value[1]"])
        
class RefBookData(models.Model):
    class Meta:
        verbose_name="Ref Book Data"
        verbose_name_plural="Ref Book Data"
    ref_book=models.ForeignKey(RefBook,verbose_name="Ref Book")
    value=TextArrayField("Value")
    
    objects=RBDManader()
    
    def __unicode__(self):
        return u"%s: %s"%(self.ref_book,self.value)
    ##
    ## Returns list of pairs (field,data)
    ##
    def _items(self):
        return zip(self.ref_book.fields,self.value)
    items=property(_items)
##
## Time Patterns
##
class TimePattern(models.Model):
    class Meta:
        verbose_name="Time Pattern"
        verbose_name_plural="Time Patterns"
    name=models.CharField("Name",max_length=64,unique=True)
    description=models.TextField("Description",null=True,blank=True)
    
    def __unicode__(self):
        return self.name
    ##
    ## Returns associated Time Pattern object
    ##
    def _time_pattern(self):
        return TP([t.term for t in self.timepatternterm_set.all()])
    time_pattern=property(_time_pattern)
    ##
    ## Matches DateTime objects against time pattern
    ##
    def match(self,d):
        return self.time_pattern.match(d)
##
## Time Pattern Terms
##
class TimePatternTerm(models.Model):
    class Meta:
        verbose_name="Time Pattern Term"
        verbose_name_plural="Time Pattern Terms"
        unique_together=[("time_pattern","term")]
    time_pattern=models.ForeignKey(TimePattern,verbose_name="Time Pattern")
    term=models.CharField("Term",max_length=256)
    
    def __unicode__(self):
        return u"%s: %s"%(self.time_pattern.name,self.term)
    ##
    ## Checks Time Pattern syntax. Raises SyntaxError in case of error
    ##
    @classmethod
    def check_syntax(cls,term):
        TP(term)
    ##
    ## Check syntax before save
    ##
    def save(self,*args):
        TimePatternTerm.check_syntax(self.term)
        super(TimePatternTerm,self).save(*args)
##
## Notification Group
##
class NotificationGroup(models.Model):
    class Meta:
        verbose_name="Notification Group"
        verbose_name_plural="Notification Groups"
        ordering=[("name")]
    name=models.CharField("Name",max_length=64,unique=True)
    description=models.TextField("Description",null=True,blank=True)
    
    def __unicode__(self):
        return self.name
    ##
    ## Returns a list of (time_pattern,method,params)
    ##
    def _members(self):
        m=[]
        # Collect user notifications
        for ngu in self.notificationgroupuser_set.filter(user__is_active=True):
            try:
                profile=ngu.user.get_profile()
            except:
                continue
            for tp,method,params in profile.contacts:
                m+=[(TimePatternList([ngu.time_pattern,tp]),method,params)]
        # Collect other notifications
        for ngo in self.notificationgroupother_set.all():
            if ngo.notification_method=="mail" and "," in ngo.params:
                for y in ngo.params.split(","):
                    m+=[(ngo.time_pattern,ngo.notification_method,y.strip())]
            else:
                m+=[(ngo.time_pattern,ngo.notification_method,ngo.params)]
        return m
    members=property(_members)
    ##
    ## Returns a set of currently active members: (method,params)
    ##
    def _active_members(self):
        now=datetime.datetime.now()
        return set([(method,param) for tp,method,param in self.members if tp.match(now)])
    active_members=property(_active_members)
    ##
    ## Send message to active members
    ##
    def notify(self,subject,body,link=None):
        for method,params in self.active_members:
            Notification(
                notification_method=method,
                notification_params=params,
                subject=subject,
                body=body,
                link=link
            ).save()
    ##
    ## Send notification to a list of groups
    ## Prevent duplicated messages
    ##
    @classmethod
    def group_notify(cls,groups,subject,body,link=None):
        ngs=set()
        for g in groups:
            for method,params in g.active_members:
                ngs.add((method,params))
        for method,params in ngs:
            Notification(
                notification_method=method,
                notification_params=params,
                subject=subject,
                body=body,
                link=link
            ).save()
##
## Users in Notification Groups
##
class NotificationGroupUser(models.Model):
    class Meta:
        verbose_name="Notification Group User"
        verbose_name_plural="Notification Group Users"
        unique_together=[("notification_group","time_pattern","user")]
    notification_group=models.ForeignKey(NotificationGroup,verbose_name="Notification Group")
    time_pattern=models.ForeignKey(TimePattern,verbose_name="Time Pattern")
    user=models.ForeignKey(User,verbose_name="User")
    
    def __unicode__(self):
        return u"%s: %s: %s"%(self.notification_group.name,self.time_pattern.name,self.user.username)
##
## Other Notification Group Items
##
NOTIFICATION_METHOD_CHOICES=[("mail","Email"),("file","File")]
USER_NOTIFICATION_METHOD_CHOICES=[("mail","Email")]

class NotificationGroupOther(models.Model):
    class Meta:
        verbose_name="Notification Group Other"
        verbose_name_plural="Notification Group Others"
        unique_together=[("notification_group","time_pattern","notification_method","params")]
    notification_group=models.ForeignKey(NotificationGroup,verbose_name="Notification Group")
    time_pattern=models.ForeignKey(TimePattern,verbose_name="Time Pattern")
    notification_method=models.CharField("Method",max_length=16,choices=NOTIFICATION_METHOD_CHOICES)
    params=models.CharField("Params",max_length=256)
    
    def __unicode__(self):
        return u"%s: %s: %s: %s"%(self.notification_group.name,self.time_pattern.name,self.notification_method,self.params)
##
##
##
class Notification(models.Model):
    class Meta:
        verbose_name="Notification"
        verbose_name_plural="Notifications"
    timestamp=models.DateTimeField("Timestamp",auto_now=True,auto_now_add=True)
    notification_method=models.CharField("Method",max_length=16,choices=NOTIFICATION_METHOD_CHOICES)
    notification_params=models.CharField("Params",max_length=256)
    subject=models.CharField("Subject",max_length=256)
    body=models.TextField("Body")
    link=models.CharField("Link",max_length=256,null=True,blank=True)
    next_try=models.DateTimeField("Next Try",null=True,blank=True)
    actual_till=models.DateTimeField("Actual Till",null=True,blank=True)
    def __unicode__(self):
        return self.subject
##
## System Notification
##
class SystemNotification(models.Model):
    class Meta:
        verbose_name="System Notification"
        verbose_name_plural="System Notifications"
    name=models.CharField("Name",max_length=64,unique=True)
    notification_group=models.ForeignKey(NotificationGroup,verbose_name="Notification Group",null=True,blank=True)
    def __unicode__(self):
        return self.name
    @classmethod
    def notify(cls,name,subject,body,link=None):
        try:
            sn=SystemNotification.objects.get(name=name)
        except SystemNotification.DoesNotExist: # Ignore undefined notifications
            return
        if sn.notification_group:
            sn.notification_group.notify(subject=subject,body=body,link=link)
##
## User Profile Manager
## Leave only current user's profile
class UserProfileManager(models.Manager):
    def get_query_set(self):
        user=get_user()
        if user:
            # Create profile when necessary
            try:
                p=super(UserProfileManager,self).get_query_set().get(user=user)
            except UserProfile.DoesNotExist:
                UserProfile(user=user).save()
            return super(UserProfileManager,self).get_query_set().filter(user=user)
        else:
            return super(UserProfileManager,self).get_query_set()
##
## User Profile
##
class UserProfile(models.Model):
    class Meta:
        verbose_name="User Profile"
        verbose_name_plural="User Profiles"
    user=models.ForeignKey(User,unique=True)
    # User data
    preferred_language=models.ForeignKey(Language,verbose_name="Preferred Language",null=True,blank=True)
    #
    objects=UserProfileManager()
    #
    def __unicode__(self):
        return "%s's Profile"%(self.user.username)
    #
    def save(self,**kwargs):
        user=get_user()
        if user and self.user!=user:
            raise Exception("Invalid user")
        super(UserProfile,self).save(**kwargs)
    ##
    ##
    ##
    def _contacts(self):
        return [(c.time_pattern,c.notification_method,c.params) for c in self.userprofilecontact_set.all()]
    contacts=property(_contacts)
    ##
    ## Returns a list of currently active contacts: (method,params)
    ##
    def _active_contacts(self):
        now=datetime.datetime.now()
        return [(c.notification_method,c.params) for c in self.contacts if c.time_pattern.match(now)]
    active_contacts=property(_active_contacts)
##
##
##
class UserProfileContact(models.Model):
    class Meta:
        verbose_name="User Profile Contact"
        verbose_name_plural="User Profile Contacts"
        unique_together=[("user_profile","time_pattern","notification_method","params")]
    user_profile=models.ForeignKey(UserProfile,verbose_name="User Profile")
    time_pattern=models.ForeignKey(TimePattern,verbose_name="Time Pattern")
    notification_method=models.CharField("Method",max_length=16,choices=USER_NOTIFICATION_METHOD_CHOICES)
    params=models.CharField("Params",max_length=256)
##
## Quarantine for automatical changes
##
class ChangesQuarantine(models.Model):
    class Meta:
        verbose_name="Changes Quarantine"
        verbose_name_plural="Changes Quarantine"
    # Quarantine types. name -> view_url
    quarantine_types={
    }
    #
    timestamp=models.DateTimeField("Timestamp",auto_now_add=True)
    changes_type=models.CharField("Type",choices=[(x,x) for x in quarantine_types],max_length=64)
    subject=models.CharField("Subject",max_length=256)
    data=PickledField("Data")
    def __unicode__(self):
        return u"%s: %s: %s"%(self.timestamp,self.changes_type,self.subject)
##
## Processing rules for changes quarantine
##
class ChangesQuarantineRule(models.Model):
    class Meta:
        verbose_name="Changes Quarantine Rule"
        verbose_name="Changes Quarantine Rules"
    name=models.CharField("Name",max_length=64,unique=True)
    is_active=models.BooleanField("Is Active",default=True)
    changes_type=models.CharField("Type",choices=[(x,x) for x in ChangesQuarantine.quarantine_types],max_length=64)
    subject_re=models.CharField("Subject",max_length=256)
    action=models.CharField("Action",max_length=1,choices=[("I","Ignore"),("A","Accept"),("Q","Quarantine")])
    description=models.TextField("Description",null=True,blank=True)
    def __unicode__(self):
        return self.name
##
## Triggers
##
def model_choices():
    for m in models.get_models():
        yield (m._meta.db_table,m._meta.db_table)
    
class DBTrigger(models.Model):
    class Meta:
        verbose_name="Database Trigger"
        verbose_name_plural="Database Triggers"
        ordering=("model","order")
    
    name=models.CharField("Name",max_length=64,unique=True)
    model=models.CharField("Model",max_length=128,choices=model_choices())
    is_active=models.BooleanField("Is Active",default=True)
    order=models.IntegerField("Order",default=100)
    description=models.TextField("Description",null=True,blank=True)
    pre_save_rule=models.ForeignKey(PyRule,verbose_name="Pre-Save Rule",
                    related_name="dbtrigger_presave_set", limit_choices_to={"interface":"IDBPreSave"},blank=True,null=True)
    post_save_rule=models.ForeignKey(PyRule,verbose_name="Post-Save Rule",
                    related_name="dbtrigger_postsave_set", limit_choices_to={"interface":"IDBPostSave"},blank=True,null=True)
    pre_delete_rule=models.ForeignKey(PyRule,verbose_name="Pre-Delete Rule",
                    related_name="dbtrigger_predelete_set", limit_choices_to={"interface":"IDBPreDelete"},blank=True,null=True)
    post_delete_rule=models.ForeignKey(PyRule,verbose_name="Post-Delete Rule",
                    related_name="dbtrigger_postdelete_set", limit_choices_to={"interface":"IDBPostDelete"},blank=True,null=True)
    ## State cache
    _pre_save_triggers={}    # model.meta.db_table -> [rules]
    _post_save_triggers={}   # model.meta.db_table -> [rules]
    _pre_delete_triggers={}  # model.meta.db_table -> [rules]
    _post_delete_triggers={} # model.meta.db_table -> [rules]
    
    def __unicode__(self):
        return u"%s: %s"%(self.model,self.name)
    
    ##
    ## Refresh triggers cache
    ##
    @classmethod
    def refresh_cache(cls,*args,**kwargs):
        # Clear cache
        cls._pre_save_triggers={}
        cls._post_save_triggers={}
        cls._pre_delete_triggers={}
        cls._post_delete_triggers={}
        # Add all active triggers
        for t in cls.objects.filter(is_active=True).order_by("order"):
            for r in ["pre_save","post_save","pre_delete","post_delete"]:
                c=getattr(cls,"_%s_triggers"%r)
                rule=getattr(t,"%s_rule"%r)
                if rule:
                    try:
                        c[t.model]+=[rule]
                    except KeyError:
                        c[t.model]=[rule]
    
    ##
    ## Dispatcher for pre-save
    ##
    @classmethod
    def pre_save_dispatch(cls,**kwargs):
        m=kwargs["sender"]._meta.db_table
        if m in cls._pre_save_triggers:
            for t in cls._pre_save_triggers[m]:
                t(model=kwargs["sender"],instance=kwargs["instance"])
    
    ##
    ## Dispatcher for post-save
    ##
    @classmethod
    def post_save_dispatch(cls,**kwargs):
        m=kwargs["sender"]._meta.db_table
        if m in cls._post_save_triggers:
            for t in cls._post_save_triggers[m]:
                t(model=kwargs["sender"],instance=kwargs["instance"],created=kwargs["created"])
    
    ##
    ## Dispatcher for pre-delete
    ##
    @classmethod
    def pre_delete_dispatch(cls,**kwargs):
        m=kwargs["sender"]._meta.db_table
        if m in cls._pre_delete_triggers:
            for t in cls._pre_delete_triggers[m]:
                t(model=kwargs["sender"],instance=kwargs["instance"])
    
    ##
    ## Dispatcher for post-delete
    ##
    @classmethod
    def post_delete_dispatch(cls,**kwargs):
        m=kwargs["sender"]._meta.db_table
        if m in cls._post_delete_triggers:
            for t in cls._post_delete_triggers[m]:
                t(model=kwargs["sender"],instance=kwargs["instance"])
    ##
    ## Called when all models are initialized
    ##
    @classmethod
    def x(cls):
        self._meta.get_field_by_name("model")[0].choices=[(m._meta.db_table,m._meta.db_table) for m in models.get_models()]

##
## Install triggers
##
if settings.IS_WEB:
    DBTrigger.refresh_cache() # Load existing triggers
    # Trigger cache syncronization
    post_save.connect(DBTrigger.refresh_cache, sender=DBTrigger)
    post_delete.connect(DBTrigger.refresh_cache, sender=DBTrigger)
    # Install signal hooks
    pre_save.connect(DBTrigger.pre_save_dispatch)
    post_save.connect(DBTrigger.post_save_dispatch)
    pre_delete.connect(DBTrigger.pre_delete_dispatch)
    post_delete.connect(DBTrigger.post_delete_dispatch)

##
## Monkeypatch to change User.username.max_length
##
User._meta.get_field("username").max_length=User._meta.get_field("email").max_length
User._meta.get_field("username").validators=[MaxLengthValidator(User._meta.get_field("username").max_length)]
