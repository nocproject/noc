# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.classificationrule application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.fm.models import EventClassificationRule
from noc.fm.models.eventclass import EventClass
from noc.lib.validators import is_objectid
from noc.fm.models import get_event
from noc.fm.models.translation import get_translated_template


class EventClassificationRuleApplication(ExtDocApplication):
    """
    EventClassificationRule application
    """
    title = "Classification Rule"
    menu = "Setup | Classification Rules"
    model = EventClassificationRule
    query_condition = "icontains"

    @view(url=r"^(?P<id>[a-z0-9]{24})/json/$", method=["GET"], api=True,
          access="read")
    def api_json(self, request, id):
        rule = self.get_object_or_404(EventClassificationRule, id=id)
        return rule.to_json()

    @view(url="^test/$", method=["POST"], access="test", api=True)
    def api_test(self, request):
        q = self.deserialize(request.raw_post_data)
        errors = []
        patterns = []
        result = False
        # Get data
        data = None
        vars = {}
        required_vars = set()
        r_patterns = []
        event_class = None
        if "data" in q:
            if is_objectid(q["data"]):
                event = get_event(q["data"])
                if event:
                    data = event.raw_vars.copy()
                    data["profile"] = event.managed_object.profile_name
                else:
                    errors += ["Event not found: %s" % q["data"]]
            else:
                # Decode json
                e = self.deserialize(q["data"])
                if isinstance(e, list):
                    e = e[0]
                if not isinstance(e, dict) or "raw_vars" not in e:
                    errors += ["Invalid JSON data"]
                else:
                    data = e["raw_vars"]
                    if "profile" in e:
                        data["profile"] = e["profile"]
        # Check event class
        if "event_class" in q:
            event_class = self.get_object_or_404(EventClass,
                                                 id=q["event_class"])
            # @todo: Get required vars
        # Check patterns
        if "patterns" in q:
            for p in q["patterns"]:
                if "key_re" in p and "value_re" in p:
                    k = None
                    v = None
                    try:
                        k = re.compile(p["key_re"])
                    except re.error, why:
                        errors += [
                            "Invalid key regular expression <<<%s>>>: %s" % (
                                p["key_re"], why)]
                    try:
                        v = re.compile(p["value_re"])
                    except re.error, why:
                        errors += [
                            "Invalid value regular expression <<<%s>>>: %s" % (
                                p["value_re"], why)]
                    if k and v:
                        patterns += [(k, v)]
        # Try to match rule
        if patterns and not errors:
            s_patterns = []
            i_patterns = []
            for pk, pv in patterns:
                matched = False
                for k in data:
                    k_match = pk.search(k)
                    if k_match:
                        v_match = pv.search(data[k])
                        if v_match:
                            # Line match
                            # Update vars
                            v = {}
                            v.update(k_match.groupdict())
                            v.update(v_match.groupdict())
                            vars.update(v)
                            # Save patterns
                            s_patterns += [{
                                "key": k,
                                "value": data[k],
                                "key_re": pk.pattern,
                                "value_re": pv.pattern,
                                "vars": [{"key": k, "value": v[k]}
                                         for k in v]
                            }]
                            matched = True
                            break
                if not matched:
                    i_patterns = [
                        {
                            "key": None,
                            "value": None,
                            "key_re": pk.pattern,
                            "value_re": pv.pattern,
                            "vars": {}
                        }
                    ]
            if s_patterns and not i_patterns:
                result = True
            r_patterns = s_patterns + i_patterns
        # @todo: Fill event class template
        if event_class:
            lang = "en"
            subject = get_translated_template(
                lang, event_class.text, "subject_template", vars)
            body = get_translated_template(
                lang, event_class.text, "body_template", vars)
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
