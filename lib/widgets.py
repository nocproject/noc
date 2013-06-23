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
## Autocomplete widget
##
class AutoCompleteTextInput(Input):
    input_type="text"
    class Media:
        css={
            "all": ["/static/css/jquery-ui.css"]
        }
        js=["/static/js/jquery-ui.min.js"]
    def __init__(self,url_name,*args,**kwargs):
        super(AutoCompleteTextInput,self).__init__(*args,**kwargs)
        self.lookup_url=url_name #reverse(url_name)
    def render(self,name,value=None,attrs=None):
        html=super(AutoCompleteTextInput,self).render(name,value,attrs)
        set_value="$(\"#%s\").val(\"%s\");"%(attrs["id"],escape(value)) if value else ""
        js="""<script type=\"text/javascript\">
        $(\"#%s\").autocomplete({minLength:3,
source: function(request,response) {
      $.ajax({
        url: \"%s\",
        data: { q: request.term  },
        success: function(data) {
	    var bb=data.split('\\n')
          response($.map(bb, function(item) {
            return { value: item   }
          }));
        }
      });
    }
});
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


class TreePopupWidget(Input):
    def render(self, name, value, attrs=None):
        if value:
            d_value = self.attrs["document"].objects.filter(id=value).first().name
            value=str(value)
        else:
            value = ""
            d_value = ""
        return mark_safe(u"""
            <input type="hidden" id="%(id)s" name="%(id)s" value="%(value)s" />
            <span id="%(id)s_text">%(d_value)s</span>
            <a href="#" onclick="show_popup_choose('%(id)s', '%(title)s', '%(lookup)s');">
                <img src="/static/img/fam/silk/resultset_next.png" />
            </a>
            """ % {"title": escape(self.attrs["title"]),
                   "lookup": self.attrs["lookup"],
                   "value": value,
                   "d_value": d_value,
                   "id": name})


class TreePopupField(forms.CharField):
    def __init__(self, document, title, lookup, required=True,
                 label=None, initial=None, help_text=None, error_messages=None,
                 show_hidden_initial=False, validators=[], localize=False):
        self.document = document
        super(TreePopupField, self).__init__(required=required, label=label,
                initial=initial, help_text=help_text,
                error_messages=error_messages,
                show_hidden_initial=show_hidden_initial,
                validators=validators,
                localize=localize,
                widget=TreePopupWidget(attrs={
                                            "title": title,
                                            "lookup": lookup,
                                            "document": document}))

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return None
        if isinstance(value, Document):
            return value
        try:
            return self.document.objects.get(id=value)
        except self.document.DoesNotExist:
            raise ValidationError("Invalid choice")

    def prepare_value(self, value):
        if isinstance(value, basestring):
            return ObjectId(value)
        return value.id if value else None

    def validate(self, value):
        return super(TreePopupField, self).validate(value)


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
