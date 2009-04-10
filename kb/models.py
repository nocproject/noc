# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Models for KB application
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.db import models
from noc.main.models import Language
from noc.main.menu import Menu
from django.contrib.auth.models import User
from noc.kb.parsers import parser_registry

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

