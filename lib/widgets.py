# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Form widgets
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django import forms
from django.http import HttpResponse
##
## Autocomplete widget
##
class AutoCompleteTextInput(forms.TextInput):
    def __init__(self,url_name,*args,**kwargs):
        super(AutoCompleteTextInput,self).__init__(*args,**kwargs)
        self.lookup_url=url_name #reverse(url_name)
    def render(self,name,value=None,attrs=None):
        from django.core.urlresolvers import reverse
        return "%s<script type=\"text/javascript\">$(\"#%s\").autocomplete(\"%s\",{minChars:3,mustMatch:1});</script>"%(
            super(AutoCompleteTextInput,self).render(name,value,attrs),attrs["id"],reverse(self.lookup_url)
        )
##
## Autocomplete lookup function:
## 
def lookup(request,func):
    result=[]
    if request.GET and "q" in request.GET:
        q=request.GET["q"]
        if len(q)>2: # Ignore requests shorter than 3 letters
            result=list(func(q))
    return HttpResponse("\n".join(result), mimetype='text/plain')
