# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface | Shutdown
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.cm.validators.text import TextValidator


class NotMatchStringValidator(TextValidator):
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
        if tpl in self.get_config_block():
            self.assert_error(
                "String in config",
                obj=error_text or template
            )
