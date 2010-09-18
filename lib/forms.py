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
##
## Bound field with django-admin like label-tag
##
class NOCBoundField(forms.forms.BoundField):
    def __init__(self,*args,**kwargs):
        super(NOCBoundField,self).__init__(*args,**kwargs)
        self.is_checkbox=isinstance(self.field.widget,forms.CheckboxInput)
        
    def label_tag(self,contents=None,attrs=None):
        if not contents:
            contents=force_unicode(escape(self.field.label)) + (u":" if not self.is_checkbox else u"")
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
    def __iter__(self):
        for name,field in self.fields.items():
            yield NOCBoundField(self,field,name)
