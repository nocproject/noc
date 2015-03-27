# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
##
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.cm.validators.text import TextValidator


class MatchAllStringsValidator(TextValidator):
    TITLE = "Config *MUST* match all string"
    DESCRIPTION = """
        Config must contain all strings in arbitrary order
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
        },
        {
            "name": "strip",
            "xtype": "checkbox",
            "boxLabel": "Strip spaces",
            "inputValue": True
        }
    ]

    def check(self, template, error_text, strip=False, **kwargs):
        tpl = self.expand_template(template)
        tpl = tpl.splitlines()
        if strip:
            tpl = [x.strip() for x in tpl]
        seen = set(x for x in tpl if x)
        for l in self.get_config_block().splitlines():
            if strip:
                l = l.strip()
            if l in seen:
                seen.remove(l)
            if not seen:
                break
        if seen:
            self.assert_error(
                "String not in config",
                obj=error_text or template
            )
