# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.db import models
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
from django.db.models.signals import class_prepared
from noc.lib.fields import TextArrayField

##
## Databrowse register hook to intersept model creation
##
def register_databrowse_model(sender,**kwargs):
    databrowse.site.register(sender)
class_prepared.connect(register_databrowse_model)
##
## Initialize download registry
##
downloader_registry.register_all()
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
                q=RefBookData.objects.filter(ref_book=b) # Filter by refbook
                ## String method
                if f.search_method=="string":
                    q=q.extra(where=["value[%d]=%%s"%f.order],params=[search])
                ## Substring method
                elif f.search_method=="substring":
                    q=q.extra(where=["value[%d] LIKE %%s"%f.order],params=["%"+search+"%"])
                ## Starting method
                elif f.search_method=="starting":
                    q=q.extra(where=["value[%d] LIKE %%s"%f.order],params=[search+"%"])
                ## MAC 3 Octets method
                elif f.search_method=="mac_3_octets_upper" and False:
                    mac=search.replace(":","").replace("-","").replace(".","")
                    if not rx_mac_3_octets.match(mac):
                        continue
                    q=q.extra(where=["value[%d]=%%s"%f.order],params=[mac])
                else:
                    return
                for r in q:
                    text="\n".join(["%s = %s"%(k,v) for k,v in zip(field_names,r.value)])
                    yield SearchResult(
                        url="/main/refbook/%d/"%b.id,
                        title="Reference Book: %s, column %s"%(b.name,f.name),
                        text=text,
                        relevancy=1.0,
                    )
##
## Ref Book Fields
##
class RefBookField(models.Model):
    class Meta:
        verbose_name="Ref Book Field"
        verbose_name="Ref Book Fields"
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
##
## Ref Book Data
##
class RefBookData(models.Model):
    class Meta:
        verbose_name="Ref Book Data"
        verbose_name_plural="Ref Book Data"
    ref_book=models.ForeignKey(RefBook,verbose_name="Ref Book")
    value=TextArrayField("Value")

##
## Application Menu
##
class AppMenu(Menu):
    app="main"
    title="Main"
    items=[
        ("Reference Books", "/main/refbook/", "is_logged_user()"),
        ("Browse Data",     "/main/databrowse/", "is_superuser()"),
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
