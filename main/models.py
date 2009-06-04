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
    #
    # Returns first free record id
    #
    def get_record_id(self):
        r=self.refbookdata_set.order_by("-record_id")[:1]
        if r:
            return r[0].record_id+1
        else:
            return 1
        
    ##
    ## Add single record
    ##
    def add_record(self,**kwargs):
        record_id=self.get_record_id()
        for f in self.refbookfield_set.all():
            if f.name in kwargs:
                RefBookData(ref_book=self,record_id=record_id,field=f,value=kwargs[f.name]).save()
        return record_id
    ##
    ## Remove single record
    ##
    def delete_record(self,record_id):
        RefBookData.objects.filter(ref_book=self,record_id=record_id).delete()
    ##
    ## Flush entire Ref Book
    ##
    def flush_refbook(self):
        RefBookData.objects.filter(ref_book=self).delete()
    ##
    ## Returns a hash containing record
    ##
    def get_record(self,record_id):
        return dict([(d.field.name,d.value) for d in RefBookData.objects.filter(ref_book=self,record_id=record_id)])
    ##
    ## Bulk upload
    ## Data is a list of hashes [{field_name:value,...},...]
    ##
    def bulk_upload(self,data):
        record_id=self.get_record_id()
        fields={}
        for f in self.refbookfield_set.all():
            fields[f.name]=f
        for r in data:
            for k,v in r.items():
                if k in fields:
                    RefBookData(ref_book=self,record_id=record_id,field=fields[k],value=v).save()
            record_id+=1
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
    ## data
    ##
    def _data(self):
        from django.db import connection
        cursor=connection.cursor()
        fields=[f.name for f in self.refbookfield_set.all()]
        field_ids=dict([(f.name,f.id) for f in self.refbookfield_set.all()])
        data_table=RefBookData._meta.db_table
        ref_book_id=self.id
        SQL="SELECT "+",".join(["f%d.value AS \"%s\""%(i,n) for i,n in enumerate(fields)])
        SQL+=" FROM %s f0 "%data_table
        for i in range(len(fields)-1):
            SQL+=" FULL JOIN %s f%d USING(record_id) "%(data_table,i+1)
        SQL+=" WHERE "+" AND ".join(["f%d.ref_book_id=%d"%(i,ref_book_id) for i,n in enumerate(fields)])
        SQL+=" AND "+" AND ".join(["f%d.field_id=%d"%(i,field_ids[n]) for i,n in enumerate(fields)])
        SQL+=" ORDER BY f0.record_id"
        cursor.execute(SQL)
        return cursor.fetchall()
    data=property(_data)
    ##
    ## Search engine plugin
    ##
    @classmethod
    def search(cls,user,search,limit):
        for b in RefBook.objects.filter(is_enabled=True):
            for f in b.refbookfield_set.filter(search_method__isnull=False):
                ## Substring method
                if f.search_method=="substring":
                    q=RefBookData.objects.filter(field=f,value__icontains=search)
                ## MAC 3 Octets method
                elif f.search_method=="mac_3_octets_upper":
                    mac=search.replace(":","").replace("-","").replace(".","")
                    if not rx_mac_3_octets.match(mac):
                        continue
                    q=RefBookData.objects.filter(field=f,value=mac[:6].upper())
                else:
                    return
                for r in q:
                    text="\n".join(["%s = %s"%(k,v) for k,v in b.get_record(r.record_id).items()])
                    yield SearchResult(
                        url="/main/refbook/%d/"%b.id,
                        title="Reference Book: %s, column %s, %s"%(b.name,f.name,r.value),
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
        choices=[("substring","substring"),("mac_3_octets_upper","3 Octets of the MAC")])
    def __unicode__(self):
        return u"%s: %s"%(self.ref_book,self.name)
##
## Ref Book Data
##
class RefBookData(models.Model):
    class Meta:
        verbose_name="Ref Book Data"
        verbose_name_plural="Ref Book Data"
        unique_together=[("ref_book","record_id","field")]
    ref_book=models.ForeignKey(RefBook,verbose_name="Ref Book")
    record_id=models.IntegerField("ID")
    field=models.ForeignKey(RefBookField,verbose_name="Field")
    value=models.TextField("Value",null=True,blank=True)

##
## Application Menu
##
class AppMenu(Menu):
    app="main"
    title="Main"
    items=[
        ("Reference Books", "/main/refbook/", "is_logged_user()"),
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
