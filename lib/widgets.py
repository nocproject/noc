# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Form widgets
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Django modules
from django import forms
from django.forms.widgets import Input
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.simplejson.encoder import JSONEncoder
from django.utils.html import escape
## Third-party modules
from tagging.models import Tag

##
##
##
class ColorPickerWidget(forms.TextInput):
    class Media:
        css={
            "all" : ["/static/css/jquery.colorPicker.css"]
        }
        js=["/static/js/jquery.colorPicker.js"]
    
    def render(self, name, value, attrs=None):
        r=super(ColorPickerWidget,self).render(name,value,attrs)
        return r+mark_safe(u"""
        <script type="text/javascript">
            $("#id_%s").colorPicker();
        </script>
        """%name)

##
## Autocomplete widget
##
class AutoCompleteTextInput(Input):
    input_type="text"
    class Media:
        css={
            "all": ["/static/css/jquery.autocomplete.css"]
        }
        js=["/static/js/jquery.autocomplete.js"]
    def __init__(self,url_name,*args,**kwargs):
        super(AutoCompleteTextInput,self).__init__(*args,**kwargs)
        self.lookup_url=url_name #reverse(url_name)
    def render(self,name,value=None,attrs=None):
        html=super(AutoCompleteTextInput,self).render(name,value,attrs)
        set_value="$(\"#%s\").val(\"%s\");"%(attrs["id"],escape(value)) if value else ""
        js="""<script type=\"text/javascript\">
        $(\"#%s\").autocomplete(\"%s\",{minChars:3,mustMatch:1});
        %s
        </script>
        """%(attrs["id"],site.reverse(self.lookup_url),set_value)
        return mark_safe("\n".join([html,js]))
##
## Autocomplete Tags
##
class AutoCompleteTags(Input):
    input_type="text"
    class Media:
        css={
            "all": ["/static/css/jquery.tokeninput.css"]
        }
        js=["/static/js/jquery.tokeninput.js"]
    def render(self,name,value=None,attrs=None):
        initial=[]
        if value:
            for v in value.split(","):
                v=v.strip()
                if v:
                    initial+=[{"id":v,"name":v}]
        initial=JSONEncoder(ensure_ascii=False).encode(initial)
        html=super(AutoCompleteTags,self).render(name,value,attrs)
        js="""<script type="text/javascript">
        $(document).ready(function() {
            $("#%s").tokenInput("%s",{
                prePopulate: %s,
                allowNewValues: true,
                canCreate: true,
                classes: {
                    tokenList: "token-input-list-noc",
                    token: "token-input-token-noc",
                    tokenDelete: "token-input-delete-token-noc",
                    selectedToken: "token-input-selected-token-noc",
                    highlightedToken: "token-input-highlighted-token-noc",
                    dropdown: "token-input-dropdown-noc",
                    dropdownItem: "token-input-dropdown-item-noc",
                    dropdownItem2: "token-input-dropdown-item2-noc",
                    selectedDropdownItem: "token-input-selected-dropdown-item-noc",
                    inputToken: "token-input-input-token-noc"
                }
                });
            });
        </script>
        """%(attrs["id"],site.reverse("main:tags:lookup"),initial)
        return mark_safe("\n".join([html,js]))
    
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

##
## Render tag list for an object
##
def tags_list(o):
    s=["<ul class='tags-list'>"]+["<li><a href='%s'>%s</a></li>"%(site.reverse("main:tags:tag",t.name),t.name) for t in Tag.objects.get_for_object(o)]+["</ul>"]
    return "".join(s)

## Load at the end to prevent circular dependencies
from noc.lib.app.site import site