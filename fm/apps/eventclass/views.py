# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Event Class Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
## NOC modules
from noc.lib.app import TreeApplication, view, HasPerm
from noc.fm.models import EventClass, EventClassVar, EventClassCategory,\
                          EventClassificationRule
from noc.lib.escape import json_escape as q


class EventClassApplication(TreeApplication):
    title = _("Event Class")
    verbose_name = _("Event Class")
    verbose_name_plural = _("Event Classes")
    menu = "Setup | Event Classes"
    model = EventClass
    category_model = EventClassCategory

    def get_preview_extra(self, obj):
        return {
            "rules": EventClassificationRule.objects.filter(event_class=obj.id).order_by("preference")
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
        r += ["        }"]
        r += ["    }"]
        r += ["]"]
        return self.render_plain_text("\n".join(r))
