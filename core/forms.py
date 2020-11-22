# ---------------------------------------------------------------------
# Forms wrapper
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.forms import Form
from django.forms.boundfield import BoundField
from django.forms.widgets import CheckboxInput
from django.utils.html import escape


# NOC modules
from noc.core.comp import smart_text


class NOCBoundField(BoundField):
    """
    Bound field with django-admin like label-tag
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_checkbox = isinstance(self.field.widget, CheckboxInput)

    def label_tag(self, contents=None, attrs=None):
        if not contents:
            contents = smart_text(escape(self.field.label if self.field.label else self.name)) + (
                ":" if not self.is_checkbox else ""
            )
        classes = []
        if self.is_checkbox:
            classes += ["vCheckboxLabel"]
        if self.field.required:
            classes += ["required"]
        if classes:
            attrs = attrs.copy() if attrs else {}
            attrs["class"] = " ".join(classes)
        return super().label_tag(contents=contents, attrs=attrs)


class NOCForm(Form):
    """
    Form wrapper returning NOCBoundField items
    """

    class Media(object):
        css = {"all": ["/ui/pkg/django-media/admin/css/forms.css"]}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.disabled_fields = set()

    def disable_field(self, name):
        self.disabled_fields.add(name)

    def __iter__(self):
        for name, field in self.fields.items():
            if name not in self.disabled_fields:
                yield NOCBoundField(self, field, name)
