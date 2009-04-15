# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Models for KB application
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.db import models
from django.db.models import Q
from noc.main.models import Language
from noc.main.menu import Menu
from django.contrib.auth.models import User
from noc.kb.parsers import parser_registry
from noc.main.search import SearchResult
from noc.lib.validators import is_int

##
## Register all wiki-syntax parsers
##
parser_registry.register_all()
##
## KB Categories
##
class KBCategory(models.Model):
    class Meta:
        verbose_name="KB Category"
        verbose_name_plural="KB Categories"
        ordering=("name",)
    name=models.CharField("Name",max_length=64,unique=True)
    def __unicode__(self):
        return self.name
##
## KB Entry
##
class KBEntry(models.Model):
    class Meta:
        verbose_name="KB Entry"
        verbose_name_plural="KB Entries"
        ordering=("id",)
    subject=models.CharField("Subject",max_length=256)
    body=models.TextField("Body")
    language=models.ForeignKey(Language,verbose_name="Language")
    markup_language=models.CharField("Markup Language",max_length="16",choices=parser_registry.choices)
    categories=models.ManyToManyField(KBCategory,verbose_name="Categories",null=True,blank=True)
    def __unicode__(self):
        return u"KB%d: %s"%(self.id,self.subject)
    ## Wiki parser class
    def _parser(self):
        return parser_registry[self.markup_language]
    parser=property(_parser)
    ## Returns parsed HTML
    def _html(self):
        return self.parser.to_html(self.body)
    html=property(_html)
    #
    def view_link(self):
        return "<A HREF='/kb/%d/'>View</A>"%self.id
    view_link.short_description="View"
    view_link.allow_tags=True
    ##
    ## Search engine
    ##
    @classmethod
    def search(cls,user,query,limit):
        if user.has_perm("kb.change_kbentry"):
            q=Q(subject__icontains=query)|Q(body__icontains=query)
            if is_int(query):
                q|=Q(id=int(query))
            elif query.startswith("KB") and is_int(query[2:]):
                q|=Q(id=int(query[2:]))
            for r in KBEntry.objects.filter(q):
                try:
                    idx=r.body.index(query)
                    text=r.body[idx-100:idx+len(query)+100]
                except ValueError:
                    text=r.body[:100]
                yield SearchResult(url="/kb/%d/"%r.id,
                    title="KB%d: %s"%(r.id,r.subject),
                    text=text,
                    relevancy=1.0)
    ##
    ## Returns latest KBEntryHistory record
    ##
    def _last_history(self):
        return self.kbentryhistory_set.order_by("-timestamp")[0]
    last_history=property(_last_history)
    ##
    ## Returns a list of last modified KB Entries
    ##
    @classmethod
    def last_modified(self,num=20):
        from django.db import connection
        c=connection.cursor()
        c.execute("SELECT kb_entry_id,MAX(timestamp) FROM kb_kbentryhistory GROUP BY 1 ORDER BY 2 DESC LIMIT %d"%num)
        return [KBEntry.objects.get(id=r[0]) for r in c.fetchall()]
    ##
    ## Write article preview log
    ##
    def log_preview(self,user):
        KBEntryPreviewLog(kb_entry=self,user=user).save()
    ##
    ## Returns preview count
    ##
    def _preview_count(self):
        return self.kbentrypreviewlog_set.count()
    preview_count=property(_preview_count)
    ##
    ## Returns most popular articles
    ##
    @classmethod
    def most_popular(self,num=20):
        from django.db import connection
        c=connection.cursor()
        c.execute("SELECT kb_entry_id,COUNT(*) FROM kb_kbentrypreviewlog GROUP BY 1 ORDER BY 2 DESC LIMIT %d"%num)
        return [KBEntry.objects.get(id=r[0]) for r in c.fetchall()]
        
##
##
##
class KBEntryHistory(models.Model):
    class Meta:
        verbose_name="KB Entry History"
        verbose_name_plural="KB Entry Histories"
        ordering=("kb_entry","timestamp")
    kb_entry=models.ForeignKey(KBEntry,verbose_name="KB Entry")
    timestamp=models.DateTimeField("Timestamp",auto_now_add=True)
    user=models.ForeignKey(User,verbose_name="User")
    diff=models.TextField("Diff")
##
##
##
class KBEntryPreviewLog(models.Model):
    class Meta:
        verbose_name="KB Entry Preview Log"
        verbose_name_plural="KB Entry Preview Log"
    kb_entry=models.ForeignKey(KBEntry,verbose_name="KB Entry")
    timestamp=models.DateTimeField("Timestamp",auto_now_add=True)
    user=models.ForeignKey(User,verbose_name="User")
    
##
## Application menu
##
class AppMenu(Menu):
    app="kb"
    title="Knowledge Base"
    items=[
        ("Knowledge Base", "/kb/", "kb.change_kbentry"),
        ("Setup",[
            ("Categories","/admin/kb/kbcategory/", "kb.change_kbcategory"),
            ("Entries",   "/admin/kb/kbentry/",    "kb.change_kbentry"),
        ])
    ]

