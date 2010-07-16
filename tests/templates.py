# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test templates
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from __future__ import with_statement
from unittest import TestCase
from noc.settings import INSTALLED_APPS
from django.template import Template,TemplateSyntaxError
import os,re
##
## Check application templates
##
class TemplatesTestCase(TestCase):
    ## Regular expressions
    rx_html_script=re.compile(r"<script.+?</script>",re.MULTILINE|re.DOTALL|re.IGNORECASE) # Scripts
    rx_html_comment=re.compile(r"<!--.+?-->",re.MULTILINE|re.DOTALL|re.IGNORECASE) # Comments
    rx_a_href=re.compile(r"<a[^>]+href=(?P<q>['\"])(?P<href>.*?)(?P=q)",re.IGNORECASE) # A HREF=
    rx_form=re.compile(r"<form[^>]+action=(?P<q>['\"])(?P<action>.*?)(?P=q)[^>]*>(?P<csrf_token>(?:\{%\s*csrf_token\s*%\})?)",re.IGNORECASE) # Form
    rx_exclude_hrefs=re.compile(r"^(/static|/media|#|\?|https?://)") # Exclude HREFS
    rx_valid_hrefs=re.compile(r"^({{.+}}|{%\s*([a-z]+_)?url.+%}|)(\?.+)?$")
    rx_breadcrumbs=re.compile(r"\{%\s*block\s+breadcrumbs\s*%\}(?P<breadcrumbs>.*?)\{%\s*endblock\s*%\}")
    rx_bc=re.compile(r"\{\{\s*block.super\s*\}\}(<li>.+?</li>)+")
    ##
    ## Check HREFS
    ##
    def check_hrefs(self,data):
        failures=[]
        for m in self.rx_a_href.finditer(data):
            href=m.group("href")
            if self.rx_exclude_hrefs.search(href):
                continue
            if not self.rx_valid_hrefs.match(href):
                failures+=["Invalid HREF '%s'"%href]
        return failures
    ##
    ## Check forms
    ##
    def check_forms(self,data):
        failures=[]
        for m in self.rx_form.finditer(data):
            action=m.group("action")
            csrf_token=m.group("csrf_token")
            if not csrf_token:
                failures+=["Form without {% csrf_token %}"]
            if self.rx_exclude_hrefs.search(action):
                continue
            if not self.rx_valid_hrefs.match(action):
                failures+=["Invalid form action '%s'"%action]
        return failures
    ##
    ## Check Breadcrumbs
    ##
    def check_breadcrumbs(self,data):
        failures=[]
        match=self.rx_breadcrumbs.search(data)
        if match:
            breadcrumbs=match.group("breadcrumbs")
            if breadcrumbs:
                if not self.rx_bc.match(breadcrumbs):
                    failures+=["Invalid breadcrumbs: %s"%breadcrumbs]
        return failures
    ##
    ## Check no {% extends admin/base.html %} in template
    ##
    def check_extends(self,data):
        failures=[]
        if "admin/base.html" in data:
            failures+=["{% extends admin/base.html %} in template"]
        return failures
    ##
    ## Check template syntax
    ##
    def check_syntax(self,data):
        failures=[]
        try:
            Template(data)
        except TemplateSyntaxError,why:
            failures+=["Syntax error: %s"%why]
        return failures
    ##
    ## Check HTML template
    ##
    def check_template(self,path):
        failures=[]
        with open(path) as f:
            data=f.read()
        data=self.rx_html_script.sub("",data)  # Wipe out scripts
        data=self.rx_html_comment.sub("",data) # Wipe out comments
        failures+=self.check_hrefs(data)
        failures+=self.check_forms(data)
        failures+=self.check_breadcrumbs(data)
        failures+=self.check_extends(data)
        failures+=self.check_syntax(data)
        return ["Error in %s: %s"%(path,m) for m in failures]
    ##
    ## Test all templates
    ##
    def test_templates(self):
        failures=[]
        # Check application templates
        for d in [x[4:] for x in INSTALLED_APPS if x.startswith("noc.")]:
            for root,dirs,files in os.walk(d):
                parts=root.split(os.path.sep)
                if parts[-1]!="templates":
                    continue
                for f in [f for f in files if f.endswith(".html")]:
                    failures+=self.check_template(os.path.join(root,f))
        assert len(failures)==0,"%d errors in templates:\n\t"%len(failures)+"\n\t".join(failures)
