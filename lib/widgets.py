# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Form widgets
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django import forms
from django.forms.widgets import Input, PasswordInput
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.core.validators import EMPTY_VALUES
# NOC modules
from lib.nosql import Document, ObjectId
from noc.lib.serialize import json_encode

##
##
##
class LabelWidget(Input):
    def render(self, name, value, attrs=None):
        return value
    

class PasswordWidget(PasswordInput):
    class Media:
        js = ["/static/js/toggle_password.js"]
    
    def render(self, name, value, attrs=None):
        r= mark_safe("<span>") + super(PasswordWidget, self).render(name, value, attrs)
        return r + mark_safe(u""" <input type="checkbox" onclick="toggle_password('id_%s',this.checked);"> Show password </span>""" % name)

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
            for v in value:
                v=v.strip()
                if v:
                    initial+=[{"id":v,"name":v}]
        initial=json_encode(initial)
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
        """%(attrs["id"], "/main/tag/ac_lookup/", initial)
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
    tags = o.tags or []
    s = (["<ul class='tags-list'>"] +
         ["<li>%s</li>" % t for t in tags] + ["</ul>"])
    return "".join(s)

## Load at the end to prevent circular dependencies
from noc.lib.app.site import site
