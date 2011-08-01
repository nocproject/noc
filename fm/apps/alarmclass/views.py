# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alarm Class Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
## NOC modules
from noc.lib.app import TreeApplication, view, HasPerm
from noc.fm.models import AlarmClass, AlarmClassCategory
from noc.lib.escape import json_escape as q


class EventClassApplication(TreeApplication):
    title = _("Alarm Class")
    verbose_name = _("Alarm Class")
    verbose_name_plural = _("Alarm Classes")
    menu = "Setup | Alarm Classes"
    model = AlarmClass
    category_model = AlarmClassCategory

    @view(url="^(?P<class_id>[0-9a-f]{24})/json/", url_name="to_json",
          access=HasPerm("view"))
    def view_to_json(self, request, class_id):
        c = AlarmClass.objects.filter(id=class_id).first()
        if not c:
            return self.response_not_found("Not found")
        r = ["["]
        r += ["    {"]
        r += ["        \"name\": \"%s\"," % q(c.name)]
        r += ["        \"desciption\": \"%s\"," % q(c.description)]
        r += ["        \"is_unique\": %s," % q(c.is_unique)]
        if c.is_unique and c.discriminator:
            r += ["        \"discriminator\": [%s]," % ", ".join(["\"%s\"" % q(d) for d in c.discriminator])]
        r += ["        \"user_clearable\": %s," % q(c.user_clearable)]
        r += ["        \"default_severity__name\": \"%s\"," % q(c.default_severity.name)]
        # datasources
        if c.datasources:
            r += ["        \"datasources\": ["]
            jds = []
            for ds in c.datasources:
                x = []
                x += ["                \"name\": \"%s\"" % q(ds.name)]
                x += ["                \"datasource\": \"%s\"" % q(ds.datasource)]
                ss = []
                for k in sorted(ds.search):
                    ss += ["                    \"%s\": \"%s\"" % (q(k), q(ds.search[k]))]
                x += ["                \"search\": {\n%s\n                }" % (",\n".join(ss))]
                jds += ["            {\n%s\n            }" % ",\n".join(x)]
            r += [",\n\n".join(jds)]
            r += ["        ]"]
        # vars
        vars = []
        for v in c.vars:
            vd = ["            {"]
            vd += ["                \"name\": \"%s\"," % q(v.name)]
            vd += ["                \"description\": \"%s\"" % q(v.description)]
            if v.default:
                vd += ["                \"default\": \"%s\"" % q(v.default)]                
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
