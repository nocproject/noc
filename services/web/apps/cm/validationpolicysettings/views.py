# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## cm.validationpolicysettings application
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.cm.models.validationpolicysettings import (
    ValidationPolicySettings, ValidationPolicyItem)
from noc.cm.models.validationpolicy import ValidationPolicy
from noc.sa.interfaces.base import (DictListParameter, DocumentParameter,
                                    BooleanParameter)


class ValidationPolicySettingsApplication(ExtDocApplication):
    """
    ValidationPolicySettings application
    """
    title = "Validation Policy Settings"
    model = ValidationPolicySettings

    MODEL_SCOPES = {
        "sa.ManagedObject": 2,
        "sa.ManagedObjectProfile": 2,
        "inv.Interface": 2,
        "inv.InterfaceProfile": 2
    }

    @view("^(?P<model_id>[^/]+)/(?P<object_id>[^/]+)/settings/$",
          method=["GET"], access="read", api=True)
    def api_get_settings(self, request, model_id, object_id):
        if model_id not in self.MODEL_SCOPES:
            return self.response_not_found("Invalid model")
        o = ValidationPolicySettings.objects.filter(
            model_id=model_id, object_id=object_id).first()
        if o:
            # Policy settings
            return [{
                "policy": str(p.policy.id),
                "policy__label": p.policy.name,
                "is_active": p.is_active
            } for p in o.policies]
        else:
            return {}

    @view("^(?P<model_id>[^/]+)/(?P<object_id>[^/]+)/settings/$",
          method=["POST"], access="read", api=True,
          validate={
              "policies": DictListParameter(attrs={
                  "policy": DocumentParameter(ValidationPolicy),
                  "is_active": BooleanParameter()
              })
          }
    )
    def api_save_settings(self, request, model_id, object_id, policies):
        def save_settings(o):
            o.save()
            return self.response({"status": True}, self.OK)

        o = ValidationPolicySettings.objects.filter(
            model_id=model_id, object_id=object_id).first()
        seen = set()
        ps = []
        for p in policies:
            if p["policy"].id in seen:
                continue
            ps += [ValidationPolicyItem(
                policy=p["policy"],
                is_active=p["is_active"]
            )]
            seen.add(p["policy"].id)
        if o:
            o.policies = ps
        else:
            o = ValidationPolicySettings(
                model_id=model_id,
                object_id=object_id,
                policies=ps
            )
        self.submit_slow_op(request, save_settings, o)
