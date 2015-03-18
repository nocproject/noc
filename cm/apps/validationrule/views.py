# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## cm.validationrule application
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.cm.models.validationrule import ValidationRule


class ValidationRuleApplication(ExtDocApplication):
    """
    ValidationRule application
    """
    title = "Validation Rule"
    menu = "Setup | Validation Rules"
    model = ValidationRule

    def field_scope(self, o):
        h = o.get_handler()
        if h:
            r = []
            if h.is_interface():
                r += ["interface"]
            if h.is_object():
                r += ["object"]
            if h.is_topology():
                r += ["topology"]
            return ", ".join(r)
        else:
            return ""

    @view(url="^config/(?P<path>.+)$", access=True, api=True)
    def api_config_form(self, request, path):
        """
        Static file server
        """
        if not path.startswith("cm/validators/") and not path.startswith("solutions/"):
            return self.response_not_found()
        return self.render_static(request, path, document_root=".")
