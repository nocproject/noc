# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Forms wrapper
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django import forms
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
##
## Bound field with django-admin like label-tag
##
class NOCBoundField(forms.forms.BoundField):
    def __init__(self,*args,**kwargs):
        super(NOCBoundField,self).__init__(*args,**kwargs)
        self.is_checkbox=isinstance(self.field.widget,forms.CheckboxInput)
        
    def label_tag(self,contents=None,attrs=None):
        if not contents:
            contents=force_unicode(escape(self.field.label if self.field.label else self.name)) + (u":" if not self.is_checkbox else u"")
        classes=[]
        if self.is_checkbox:
            classes+=[u"vCheckboxLabel"]
        if self.field.required:
            classes+=[u"required"]
        if classes:
            attrs=attrs.copy() if attrs else {}
            attrs["class"]=u" ".join(classes)
        return super(NOCBoundField,self).label_tag(contents=contents, attrs=attrs)
##
## Form wrapper returning NOCBoundField items
##
class NOCForm(forms.Form):
    class Media:
        css={
            "all" : ["/media/css/forms.css"],
        }
    def __init__(self,*args,**kwargs):
        super(NOCForm,self).__init__(*args,**kwargs)
        self.disabled_fields=set()
    
    def disable_field(self,name):
        self.disabled_fields.add(name)
    
    def __iter__(self):
        for name,field in self.fields.items():
            if name not in self.disabled_fields:
                yield NOCBoundField(self,field,name)
    
##
## Login form base class
##
class NOCAuthenticationForm(NOCForm):
    def __init__(self,request=None,*args,**kwargs):
        self.user_cache=request
        self.request=None
        super(NOCAuthenticationForm,self).__init__(*args,**kwargs)
    
    def clean(self):
        # Check all required fields present, then try to authenticate
        passed=True
        for n,f in self.fields.items():
            if f.required and n not in self.cleaned_data or not self.cleaned_data[n]:
                passed=False
                break
        # Try to authenticate
        if passed:
            self.user_cache=authenticate(**self.cleaned_data)
            if self.user_cache is None:
                # Authentication failed
                raise forms.ValidationError(_("Authentication failed"))
            if not self.user_cache.is_active:
                # Disabled user
                raise forms.ValidationError(_("This account is inactive"))
        
        # Check cookies is working
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError(_("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in."))
        return self.cleaned_data
    
    def get_user(self):
        return self.user_cache
    