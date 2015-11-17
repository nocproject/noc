# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Config *MUST* match string
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.cm.validators.text import TextValidator


class MatchStringRE(TextValidator):
    TITLE = "Config *MUST* match re"
    DESCRIPTION = """
        Config must match regular expression
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
        try:
            rx = re.compile(tpl, re.DOTALL | re.MULTILINE)
        except:
            return
        if not rx.search(self.get_config_block()):
            if self.scope == self.INTERFACE:
                obj = self.object.name
            else:
                obj = None
            self.assert_error(
                "Config | Mismatch Template",
                obj=obj,
                msg=error_text or template
            )
