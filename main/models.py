# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.db import models
from django.contrib.auth.models import User
from noc.main.report import report_registry
from noc.main.menu import populate_reports
from noc.main.menu import Menu
from noc.lib.fields import BinaryField
from noc.lib.database_storage import DatabaseStorage as DBS
import noc.main.search # Set up signal handlers
import os,datetime,re
from noc.main.refbooks.downloaders import downloader_registry
from noc.main.search import SearchResult
from django.contrib import databrowse
from django.db.models.signals import class_prepared,pre_save,pre_delete
from noc.lib.fields import TextArrayField
from noc.main.middleware import get_user
from noc.settings import IS_WEB

##
## Databrowse register hook to intersept model creation
##
def register_databrowse_model(sender,**kwargs):
    databrowse.site.register(sender)
class_prepared.connect(register_databrowse_model)
##
## Exclude tables from audit
##
AUDIT_TRAIL_EXCLUDE={
    "django_admin_log"    : None,
    "django_session"      : None,
    "auth_message"        : None,
    "main_audittrail"     : None,
    "kb_kbentryhistory"   : None,
    "kb_kbentrypreviewlog": None,
}
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
        old=sender.objects.get(id=instance.id)
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
if IS_WEB:
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
        AuditTrail(
            user=user,
            model=sender.__name__,
            db_table=sender._meta.db_table,
            operation=operation,
            subject=str(instance),
            body=message
        ).save()
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
                        url="/main/refbook/%d/"%b.id,
                        title="Reference Book: %s, column %s"%(b.name,f.name),
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
            "where" : ["value[%d]=%%s"%self.order],
            "params": [search]
        }
    # Substring match
    def search_substring(self,search):
        return {
            "where" : ["value[%d] LIKE %%s"%self.order],
            "params": ["%"+search+"%"]
        }
    # Starting
    def search_starting(self,search):
        return {
            "where" : ["value[%d] LIKE %%s"%self.order],
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
## Application Menu
##
class AppMenu(Menu):
    app="main"
    title="Main"
    items=[
        ("Audit Trail",    "/admin/main/audittrail/", "is_superuser()"),
        ("Reference Books", "/main/refbook/",          "is_logged_user()"),
        ("Browse Data",     "/main/databrowse/",       "is_superuser()"),
        ("Setup", [
            ("Users",  "/admin/auth/user/",  "auth.change_user"),
            ("Groups", "/admin/auth/group/", "auth.change_group"),
            ("Languages","/admin/main/language/", "main.change_language"),
            ("MIME Types", "/admin/main/mimetype/", "main.change_mimetype"),
            ("Configs",    "/main/config/",  "is_superuser()"),
            ("Reference Books", "/admin/main/refbook/", "main.change_refbook"),
        ]),
        ("Documentation", [
            ("Administrator's Guide", "/static/doc/en/ag/html/index.html"),
            ("User's Guide", "/static/doc/en/ug/html/index.html"),
        ]),
    ]
##
## Load and register reports
##
report_registry.register_all()
populate_reports([(n,r.title) for n,r in report_registry.classes.items()])
