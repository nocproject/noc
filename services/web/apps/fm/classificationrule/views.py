# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.classificationrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# Django modules
from django.template import Template, Context
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.fm.models.eventclassificationrule import EventClassificationRule, EventClassificationRuleCategory
from noc.fm.models.eventclass import EventClass
from noc.fm.models.mib import MIB
from noc.lib.validators import is_objectid, is_oid
from noc.fm.models.utils import get_event
from noc.core.translation import ugettext as _


class EventClassificationRuleApplication(ExtDocApplication):
    """
    EventClassificationRule application
    """
    title = _("Classification Rule")
    menu = [_("Setup"), _("Classification Rules")]
    model = EventClassificationRule
    parent_model = EventClassificationRuleCategory
    parent_field = "parent"
    query_condition = "icontains"

    @view(url="^test/$", method=["POST"], access="test", api=True)
    def api_test(self, request):
        q = self.deserialize(request.raw_post_data)
        errors = []
        patterns = []
        result = False
        # Get data
        data = {}
        vars = {}
        required_vars = set()
        r_patterns = []
        event_class = None
        subject = None
        body = None
        if "data" in q:
            if is_objectid(q["data"]):
                event = get_event(q["data"])
                if event:
                    data = event.raw_vars.copy()
                    data["profile"] = event.managed_object.profile.name
                    data["source"] = event.source
                else:
                    errors += ["Event not found: %s" % q["data"]]
            else:
                # Decode json
                try:
                    e = self.deserialize(q["data"])
                except Exception:
                    errors += ["Cannot decode JSON"]
                    e = None
                if isinstance(e, list):
                    e = e[0]
                if not isinstance(e, dict) or "raw_vars" not in e:
                    errors += ["Invalid JSON data"]
                else:
                    data = e["raw_vars"]
                    if "profile" in e:
                        data["profile"] = e["profile"]
                    if "source" in e:
                        data["source"] = e["source"]
            if data.get("source") == "SNMP Trap":
                # Resolve MIBs
                data.update(MIB.resolve_vars(data))
        # Check event class
        if "event_class" in q:
            event_class = self.get_object_or_404(EventClass,
                                                 id=q["event_class"])
            for v in event_class.vars:
                if v.required:
                    required_vars.add(v.name)
                    vars[v.name] = "MISSED!"
        # Check patterns
        if "patterns" in q:
            for p in q["patterns"]:
                if "key_re" in p and "value_re" in p:
                    k = None
                    v = None
                    try:
                        k = re.compile(p["key_re"])
                    except re.error as why:
                        errors += [
                            "Invalid key regular expression <<<%s>>>: %s" % (
                                p["key_re"], why)]
                    try:
                        v = re.compile(p["value_re"])
                    except re.error as why:
                        errors += [
                            "Invalid value regular expression <<<%s>>>: %s" % (
                                p["value_re"], why)]
                    if k and v:
                        patterns += [(k, v)]
        # Try to match rule
        if patterns and not errors:
            s_patterns = []
            i_patterns = []
            for pkey, pvalue in patterns:
                matched = False
                for k in data:
                    k_match = pkey.search(k)
                    if k_match:
                        v_match = pvalue.search(data[k])
                        if v_match:
                            # Line match
                            # Update vars
                            v = {}
                            v.update(k_match.groupdict())
                            v.update(v_match.groupdict())
                            vars.update(v)
                            # Save patterns
                            s_patterns += [{
                                "status": True,
                                "key": k,
                                "value": data[k],
                                "key_re": pkey.pattern,
                                "value_re": pvalue.pattern,
                                "vars": [{"key": k, "value": v[k]}
                                         for k in v]
                            }]
                        else:
                            i_patterns += [
                                {
                                    "status": False,
                                    "key": k,
                                    "value": data[k],
                                    "key_re": pkey.pattern,
                                    "value_re": pvalue.pattern,
                                    "vars": {}
                                }
                            ]
                        matched = True
                        break
                if not matched:
                    i_patterns += [
                        {
                            "status": False,
                            "key": None,
                            "value": None,
                            "key_re": pkey.pattern,
                            "value_re": pvalue.pattern,
                            "vars": {}
                        }
                    ]
            if s_patterns and not i_patterns:
                result = True
            r_patterns = s_patterns + i_patterns
        # Calculate rule variables
        if "vars" in q and q["vars"]:
            for v in q["vars"]:
                if v["value"].startswith("="):
                    # Evaluate
                    try:
                        vars[v["name"]] = eval(v["value"][1:], {}, vars)
                    except Exception as why:
                        errors += [
                            "Error when evaluating '%s': %s" % (v["name"], why)
                        ]
                else:
                    vars[v["name"]] = v["value"]
        # Check required variables
        for rvars in required_vars:
            if rvars not in vars:
                errors += ["Missed required variable: %s" % rvars]
        # Fill event class template
        if event_class:
            # lang = "en"
            ctx = Context(vars)
            subject = Template(event_class.subject_template).render(ctx)
            body = Template(event_class.body_template).render(ctx)
        # Check expression
        r = {
            "result": result
        }
        if errors:
            r["errors"] = errors
        if vars:
            r["vars"] = [{"key": k, "value": vars[k]} for k in vars]
        if r_patterns:
            r["patterns"] = r_patterns
        if subject:
            r["subject"] = subject
        if body:
            r["body"] = body
        return r

    @view(url="^from_event/(?P<event_id>[0-9a-f]{24})/$",
          method=["GET"], access="create", api=True)
    def api_from_event(self, request, event_id):
        """
        Create classification rule from event
        :param request:
        :param event_id:
        :return:
        """
        event = get_event(event_id)
        if not event:
            self.response_not_found()
        event_name = " | ".join(event.managed_object.profile.name.split(".")) + " | <name> "
        if event.source == "syslog":
            event_name += "(SYSLOG)"
        elif event.source == "SNMP Trap":
            event_name += "(SNMP)"
        data = {
            "name": event_name,
            "preference": 1000
        }
        if event.source == "syslog":
            data["description"] = event.raw_vars["message"]
        elif (event.source == "SNMP Trap" and
              "SNMPv2-MIB::snmpTrapOID.0" in event.resolved_vars):
            data["description"] = event.resolved_vars["SNMPv2-MIB::snmpTrapOID.0"]
        patterns = {}
        for k in event.raw_vars:
            if k not in ("collector", "facility", "severity"):
                patterns[k] = event.raw_vars[k]
        if hasattr(event, "resolved_vars"):
            for k in event.resolved_vars:
                if k not in (
                        "RFC1213-MIB::sysUpTime.0",
                        "SNMPv2-MIB::sysUpTime.0") and not is_oid(k):
                    patterns[k] = event.resolved_vars[k]
        data["patterns"] = [
            {
                "key_re": "^%s$" % k,
                "value_re": "^%s$" % patterns[k]
            } for k in patterns
        ]
        return data
