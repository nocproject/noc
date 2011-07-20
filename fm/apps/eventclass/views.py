# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Event Class Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django import forms
## NOC modules
from noc.lib.app import TreeApplication, view, HasPerm
from noc.fm.models import EventClass, EventClassVar, EventClassCategory,\
                          EventClassificationRule
from noc.lib.escape import json_escape as q
from noc.lib.forms import NOCForm


class EventClassApplication(TreeApplication):
    title = _("Event Class")
    verbose_name = _("Event Class")
    verbose_name_plural = _("Event Classes")
    menu = "Setup | Event Classes"
    model = EventClass
    category_model = EventClassCategory

    def get_preview_extra(self, obj):
        l = obj.text.keys()
        languages = []
        if "en" in l:
            languages += ["en"]
            l.remove("en")
        languages += sorted(l)
        text = []
        for l in languages:
            t = {"language": l}
            for k, v in obj.text[l].items():
                t[k] = v
            text += [t]
        return {
            "rules": EventClassificationRule.objects.filter(event_class=obj.id).order_by("preference"),
            "text": text
        }

    @view(url="^(?P<class_id>[0-9a-f]{24})/json/", url_name="to_json",
          access=HasPerm("view"))
    def view_to_json(self, request, class_id):
        c = EventClass.objects.filter(id=class_id).first()
        if not c:
            return self.response_not_found("Not found")
        r = ["["]
        r += ["    {"]
        r += ["        \"name\": \"%s\"," % q(c.name)]
        r += ["        \"desciption\": \"%s\"," % q(c.description)]
        r += ["        \"action\": \"%s\"," % q(c.action)]
        # vars
        vars = []
        for v in c.vars:
            vd = ["            {"]
            vd += ["                \"name\": \"%s\"," % q(v.name)]
            vd += ["                \"description\": \"%s\"," % q(v.description)]
            vd += ["                \"type\": \"%s\"," % q(v.type)]
            vd += ["                \"required\": %s," % q(v.required)]
            vd += ["            }"]
            vars += ["\n".join(vd)]
        r += ["        \"vars \": ["]
        r += [",\n\n".join(vars)]
        r += ["        ],"]
        # text
        r += ["        \"text\": {"]
        t = []
        for lang in c.text:
            l = ["            \"%s\": {" % lang]
            ll = []
            for v in ["subject_template", "body_template", "symptoms",
                      "probable_causes", "recommended_actions"]:
                if v in c.text[lang]:
                    ll += ["                \"%s\": \"%s\"" % (v, q(c.text[lang][v]))]
            l += [",\n".join(ll)]
            l += ["            }"]
            t += ["\n".join(l)]
        r += [",\n\n".join(t)]
        # Disposition rules
        if c.disposition:
            r += ["        },"]
            r += ["        \"disposition\": ["]
            l = []
            for d in c.disposition:
                ll = ["            {"]
                lll = ["                \"name\": \"%s\"" % q(d.name)]
                lll += ["                \"condition\": \"%s\"" % q(d.condition)]
                lll += ["                \"action\": \"%s\"" % q(d.action)]
                if d.alarm_class:
                    lll += ["                \"alarm_class__name\": \"%s\"" % q(d.alarm_class.name)]
                ll += [",\n".join(lll)]
                ll += ["            }"]
                l += ["\n".join(ll)]
            r += [",\n".join(l)]
            r += ["        ]"]
        r += ["    }"]
        r += ["]"]
        return self.render_plain_text("\n".join(r))

    class EventClassForm(NOCForm):
        name = forms.CharField(label="Name")
        description = forms.CharField(label="Description")
        action = forms.ChoiceField(label="Action",
                                   choices=[
                                        ("D", "Drop"),
                                        ("L", "Log"),
                                        ("A", "Log and Archive")])

    class TextForm(forms.Form):
        language = forms.CharField(label="Language")
        subject_template = forms.CharField(label="Subject Template")
        body_template = forms.CharField(label="Body Template",
                                widget=forms.TextInput())
        symptoms = forms.CharField(label="Symptoms",
                                widget=forms.TextInput())
        probable_causes = forms.CharField(label="Probable Causes",
                                widget=forms.TextInput())
        recommended_actions = forms.CharField(label="Recommended Actions",
                                widget=forms.TextInput())

    class VarsForm(forms.Form):
        pass

    def process_change_form(self, request, object_id=None,
                            form_initial=None, formset_initial=None):
        # Fetch object when in edit mode
        event_class = None
        if object_id:
            event_class = EventClass.objects.filter(id=object_id).first()
            if not event_class:
                return self.response_not_found("Event class not found")
        if request.POST:
            pass
        elif event_class:
            pass
        else:
            # New
            form = self.EventClassForm()
            TextFormset = forms.formsets.formset_factory(self.TextForm,
                                                         can_delete=True,
                                                         extra=3)
            vars_formset = None
            rules_formset = None
            text_formset = TextFormset()
        return self.render(request, "edit.html", form=form,
                           vars_formset=vars_formset,
                           rules_formset=rules_formset,
                           text_formset=text_formset,
                           object_id=object_id)

    
    

    @view(url="^add/$", url_name="add", access=HasPerm("change"))
    def view_add(self, request):
        return self.process_change_form(request)

    @view(url="^(?P<object_id>[0-9a-f]{24})/change/$", url_name="change",
          access=HasPerm("change"))
    def view_change(self, request, object_id):
        return self.process_change_form(request, object_id)

    @view(url="^(?P<object_id>[0-9a-f]{24})/delete/$",
          url_name="delete", access=HasPerm("change"))
    def view_delete(self, request, object_id):
        o = EventClass.objects.filter(id=object_id).first()
        if not o:
            return self.response_not_found("Not found")
        o.delete()
        self.message_user(request, "Event Class has beed deleted")
        return self.response_redirect("fm:eventclass:tree")
