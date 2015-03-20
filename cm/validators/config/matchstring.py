# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface | Shutdown
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.cm.validators.text import TextValidator


class MatchStringValidator(TextValidator):
    TITLE = "Config *MUST* match string"
    DESCRIPTION = """
        Config must contain exact string
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
        if tpl not in self.object_config:
            self.assert_error(
                "String not in config",
                obj=error_text or template
            )
