# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Forms wrapper
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django import forms
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _


class NOCBoundField(forms.forms.BoundField):
    """
    Bound field with django-admin like label-tag
    """
    def __init__(self, *args, **kwargs):
        super(NOCBoundField, self).__init__(*args, **kwargs)
        self.is_checkbox = isinstance(self.field.widget,
            forms.CheckboxInput)

    def label_tag(self, contents=None, attrs=None):
        if not contents:
            contents = force_unicode(escape(
                self.field.label if self.field.label else self.name)) + (
            u":" if not self.is_checkbox else u"")
        classes = []
        if self.is_checkbox:
            classes += [u"vCheckboxLabel"]
        if self.field.required:
            classes += [u"required"]
        if classes:
            attrs = attrs.copy() if attrs else {}
            attrs["class"] = u" ".join(classes)
        return super(NOCBoundField, self).label_tag(contents=contents,
            attrs=attrs)


class NOCForm(forms.Form):
    """
    Form wrapper returning NOCBoundField items
    """
    class Media:
        css = {
            "all": ["/media/admin/css/forms.css"],
            }

    def __init__(self, *args, **kwargs):
        super(NOCForm, self).__init__(*args, **kwargs)
        self.disabled_fields = set()

    def disable_field(self, name):
        self.disabled_fields.add(name)

    def __iter__(self):
        for name, field in self.fields.items():
            if name not in self.disabled_fields:
                yield NOCBoundField(self, field, name)
