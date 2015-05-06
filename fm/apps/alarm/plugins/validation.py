# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ValidationPlugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.template import Template, Context
## NOC modules
from base import AlarmPlugin
from noc.cm.models.objectfact import ObjectFact
from noc.cm.models.errortype import ErrorType


class ValidationPlugin(AlarmPlugin):
    name = "validation"

    def get_data(self, alarm, config):
        r = {
            "plugins": [("NOC.fm.alarm.plugins.Validation", {})],
            "validation_errors": []
        }
        t_cache = {}
        for f in ObjectFact.objects.filter(
                object=alarm.managed_object.id,
                cls="error").order_by("introduced"):
            etn = f.attrs.get("type")
            if etn:
                et = t_cache.get(etn)
                if not et:
                    et = ErrorType.objects.filter(name=etn).first()
                    t_cache[etn] = et
                subject = Template(et.subject_template).render(Context(f.attrs))
                body = Template(et.body_template).render(Context(f.attrs))
            else:
                subject = etn
                body = etn

            r["validation_errors"] += [{
                "uuid": str(f.uuid),
                "introduced": f.introduced.isoformat(),
                "changed": f.changed.isoformat(),
                "subject": subject,
                "body": body,
                "cls": etn,
                "attrs": f.attrs
            }]
        return r
