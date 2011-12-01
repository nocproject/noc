# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Event Classification Rule Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## Django modules
from django.utils.translation import ugettext_lazy as _
from django import forms
## NOC modules
from noc.lib.app import TreeApplication, view, HasPerm
from noc.lib.forms import NOCForm
from noc.lib.widgets import TreePopupField
from noc.fm.models import EventClassificationRule,\
                          EventClassificationRuleCategory,\
                          EventClass, EventClassificationPattern,\
                          get_event
from noc.lib.escape import json_escape as q
from noc.lib.text import indent


class ClassificationRuleApplication(TreeApplication):
    title = _("Classification Rule")
    verbose_name = _("Classification Rule")
    verbose_name_plural = _("Classification Rules")
    menu = "Setup | Classification Rules"
    model = EventClassificationRule
    category_model = EventClassificationRuleCategory

    rx_re_quote=re.compile(r"[()\[\].+*?^$]", re.MULTILINE)
    rx_oid = re.compile(r"^(\d+\.){5,}\d+$")
    rx_heading = re.compile(r"^\^.+?(?=%[A-Z0-9])")
    rx_ip = re.compile(r"[0-9]{,3}\\\.[0-9]{,3}\\\.[0-9]{,3}\\\.[0-9]{,3}")
    rx_object_id = re.compile("^[0-9a-f]{24}$")
    
    @view(url="^(?P<rule_id>[0-9a-f]{24})/to_json/$",
          url_name="to_json", access=HasPerm("to_json"))
    def view_to_json(self, request, rule_id):
        """
        Render classification rule as JSON, ready to include
        into the NOC distribution
        """
        rule = EventClassificationRule.objects.filter(id=rule_id).first()
        if not rule:
            return self.response_not_found()
        r = ["["]
        r += [indent(rule.to_json(), 4)]
        r += ["]",""]
        return self.render_plain_text("\n".join(r))

    class RulePatternForm(forms.Form):
        key_re = forms.CharField(required=True,
                                 widget=forms.TextInput(attrs={"size": "80"}))
        value_re = forms.CharField(required=True,
                                   widget=forms.TextInput(attrs={"size": "80"}))
    
    class RuleForm(NOCForm):
        name = forms.CharField(label="Name")
        description = forms.CharField(label="Description",
                                      widget=forms.widgets.Textarea)
        event_class = TreePopupField(label="Event Class",
                                     document=EventClass,
                                     title="Select Event Class",
                                     lookup="/fm/eventclass/popup/"
                                     )
        preference = forms.IntegerField(label="Preference")

    def process_change_form(self, request, object_id=None,
                            form_initial=None, formset_initial=None):
        # Fetch object when in edit mode
        rule = None
        if object_id:
            rule = EventClassificationRule.objects.filter(id=object_id).first()
            if not rule:
                return self.response_not_found("Rule not found")
        RulePatternFormset = forms.formsets.formset_factory(self.RulePatternForm,
                                                            can_delete=True,
                                                            extra=5)
        if request.POST:
            form = self.RuleForm(request.POST)
            formset = RulePatternFormset(request.POST)
            if form.is_valid() and formset.is_valid():
                if rule is None:
                    rule = EventClassificationRule()
                rule.name = form.cleaned_data["name"]
                rule.is_builtin = False
                rule.description = form.cleaned_data["description"]
                rule.event_class = form.cleaned_data["event_class"]
                rule.preference = form.cleaned_data["preference"]
                rule.patterns = [EventClassificationPattern(
                                key_re=f.cleaned_data["key_re"],
                                value_re=f.cleaned_data["value_re"])
                          for f in formset
                          if ("key_re" in f.cleaned_data and
                              "value_re" in f.cleaned_data and
                              not f.cleaned_data["DELETE"])]
                rule.save()
                self.message_user(request, "Classification rule has been changed")
                return self.response_redirect("fm:classificationrule:preview", rule.id)
        elif rule:
            form = self.RuleForm({
                "name": rule.name,
                "description": rule.description,
                "preference": rule.preference,
                "event_class": rule.event_class
                })
            formset = RulePatternFormset(initial=([
                {
                    "key_re": p.key_re,
                    "value_re": p.value_re
                } for p in rule.patterns]))
        else:
            form = self.RuleForm(form_initial or {
                "name": "Rule name",
                "description": "Place rule description here",
                "preference": 1000
                })
            formset = RulePatternFormset(initial=formset_initial or [
                {
                    "key_re": "^source$",
                    "value_re": ".+"
                },
                {
                    "key_re": "^profile$",
                    "value_re": ".+"
                }])
        return self.render(request, "edit.html", form=form, formset=formset,
                           object_id=object_id)
        
    @view(url="^add/$", url_name="add", access=HasPerm("change"))
    def view_add(self, request):
        return self.process_change_form(request)

    @view(url="^(?P<object_id>[0-9a-f]{24})/change/$", url_name="change",
          access=HasPerm("change"))
    def view_change(self, request, object_id):
        return self.process_change_form(request, object_id)
    
    @view(url="^add/event/(?P<event_id>[0-9a-f]{24})/$", url_name="from_event",
          access=HasPerm("change"))
    def view_from_event(self, request, event_id):
        def re_q(s):
            return self.rx_re_quote.sub(lambda x: "\\" + x.group(0), s).replace("\n", "\\n")

        def p(k, v):
            v = "^%s$" % re_q(v)
            if event.raw_vars["source"] == "syslog" and k == "message":
                v = self.rx_heading.sub("", v)
                v = self.rx_ip.sub(r"(?P<ip>\S+)", v)
            return {
                "key_re": "^%s$" % re_q(k),
                "value_re": v
            }

        def is_oid(v):
            return self.rx_oid.match(v) is not None
        
        event = get_event(event_id)
        if event is None:
            return self.response_not_found("Not found")
        event_name = " | ".join(event.managed_object.profile_name.split("."))
        event_name += " | <name> "
        if event.raw_vars["source"] == "syslog":
            event_name += "(SYSLOG)"
        elif event.raw_vars["source"] == "SNMP Trap":
            event_name += "(SNMP)"
        form_initial = {
            "name": event_name,
            "preference": 1000
            }
        if event.raw_vars["source"] == "syslog":
            form_initial["description"] = event.raw_vars["message"]
        elif (event.raw_vars["source"] == "SNMP Trap" and
              "SNMPv2-MIB::snmpTrapOID.0" in event.resolved_vars):
            form_initial["description"] = event.resolved_vars["SNMPv2-MIB::snmpTrapOID.0"]
        initial = [(k, v)
            for k, v in event.raw_vars.items()
            if k not in ("collector", "facility", "severity") and not is_oid(k)
            ]
        if hasattr(event, "resolved_vars"):
            initial += [(k, v)
                for k, v in event.resolved_vars.items()
                if k not in ("RFC1213-MIB::sysUpTime.0",
                             "SNMPv2-MIB::sysUpTime.0")]
        initial = dict(initial)
        lkeys = initial.keys()
        keys = []
        for k in ("source", "profile"):
            if k in lkeys:
                keys += [k]
                lkeys.remove(k)
        keys += sorted(lkeys)
        formset_initial = [p(k, initial[k]) for k in keys]
        return self.process_change_form(request, form_initial=form_initial,
                                        formset_initial=formset_initial)

    @view(url="^(?P<object_id>[0-9a-f]{24})/delete/$",
          url_name="delete", access=HasPerm("change"))
    def view_delete(self, request, object_id):
        o = EventClassificationRule.objects.filter(id=object_id).first()
        if not o:
            return self.response_not_found("Not found")
        o.delete()
        self.message_user(request, "Rule has beed deleted")
        return self.response_redirect("fm:classificationrule:tree")

    @view(url="^(?P<object_id>[0-9a-f]{24})/test_re/(?P<part>[KV])/(?P<line>\d+)/$",
          url_name="test_re", access=HasPerm("change"))
    def view_test_re(self, request, object_id, part, line):
        """
        Test RE popup handler
        """
        o = EventClassificationRule.objects.filter(id=object_id).first()
        if not o:
            return self.response_not_found("Not found")
        line = int(line)
        if line >= len(o.patterns):
            return self.response_not_found("Line not found")
        to_reload = False
        longest_matched = ""
        longest_matched_re = ""
        if request.POST:
            rx = request.POST.get("rx")
            value = request.POST.get("value")
            status = False
            vars = None
            if rx and value:
                try:
                    rxc = re.compile(rx, re.MULTILINE | re.DOTALL)
                except:
                    rxc = None
                if rxc:
                    match = rxc.search(value)
                    if match:
                        status = True
                        vars = match.groupdict()
                    else:
                        # Find longest matched part of regular expression
                        longest_matched_re = rx
                        while longest_matched_re:
                            longest_matched_re = longest_matched_re[:-1]
                            try:
                                rxl = re.compile(longest_matched_re,
                                                 re.MULTILINE | re.DOTALL)
                            except:
                                continue
                            match = rxl.search(value)
                            if match:
                                longest_matched = value[match.start():match.end()]
                                break
                    if "_update" in request.POST:
                        # Fix regular expression
                        p = o.patterns[line]
                        if part == "K":
                            p.key_re = rx
                        else:
                            p.value_re = rx
                        o.save()
                        self.message_user(request, "Rule pattern has been updated")
                        to_reload = True
        else:
            p = o.patterns[line]
            rx = p.key_re if part == "K" else p.value_re
            status = False
            vars = None
            value = ""
        return self.render(request, "test_re.html", rx=rx,
                           status=status, vars=vars, value=value,
                           to_reload=to_reload,
                           longest_matched_re=longest_matched_re,
                           longest_matched=longest_matched)
    
    @view(url=r"(?P<object_id>[0-9a-f]{24})/test_event/$", url_name="test_event",
          access=HasPerm("change"))
    def view_test_event(self, request, object_id):
        o = EventClassificationRule.objects.filter(id=object_id).first()
        if not o:
            return self.response_not_found("Not found")
        event = ""
        r = []  # style, key, value, key_re, value_re
        rv = {}
        result = None
        not_found = False
        if request.POST and "event" in request.POST:
            event_oid = request.POST["event"].strip()
            if self.rx_object_id.match(event_oid):
                event = get_event(event_oid)
            else:
                event = ""
            if event:
                vars = event.raw_vars.copy()
                if hasattr(event, "resolved_vars"):
                    vars.update(event.resolved_vars)
                patterns = dict([(p.key_re, p.value_re) for p in o.patterns])
                # Match
                for pk, pv in patterns.items():
                    rpk = re.compile(pk, re.MULTILINE | re.DOTALL)
                    rpv = re.compile(pv, re.MULTILINE | re.DOTALL)
                    for k, v in vars.items():
                        mk = rpk.search(k)
                        if mk:
                            mv = rpv.search(v)
                            if mv:
                                rv.update(mk.groupdict())
                                rv.update(mv.groupdict())
                                r += [["matched", k, v, pk, pv]]
                                del patterns[pk]
                                del vars[k]
                # Mismatched rules
                result = len(patterns) == 0
                for pk, pv in patterns.items():
                    r += [["mismatched", "", "", pk, pv]]
                # Mismatched vars
                for k, v in vars.items():
                    r += [["rest", k, v, "", ""]]
            else:
                not_found = True
        return self.render(request, "test_event.html", event=event, r=r, rv=rv,
                           result=result, not_found=not_found)
