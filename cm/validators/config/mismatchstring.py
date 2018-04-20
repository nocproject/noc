# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Config *MUST NOT* match string
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## Config *MUST NOT* match string
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.cm.validators.text import TextValidator


class MismatchStringValidator(TextValidator):
    TITLE = "Config *MUST NOT* match string"
    DESCRIPTION = """
        Config must not contain exact string
    """
    CONFIG_FORM = [
        {
            "name": "template",
            "xtype": "textarea",
            "fieldLabel": "Template",
            "allowBlank": False
        },
        {
            "name": "error_text",
            "xtype": "textarea",
            "fieldLabel": "Error text",
            "allowBlank": True
        }
    ]

    def check(self, template, error_text, **kwargs):
        tpl = self.expand_template(template)
        if tpl not in self.get_config_block():
            if self.scope == self.INTERFACE:
                obj = self.object.name
            else:
                obj = None
            self.assert_error(
                "Config | Match Template",
                obj=obj,
                msg=error_text or template
            )
