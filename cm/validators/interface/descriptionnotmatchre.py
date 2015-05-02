# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface description *MUST NOT MATCH* regexp
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.cm.validators.clipsinterface import CLIPSInterfaceValidator


class InterfaceDescriptionNotMatchRegexpValidator(CLIPSInterfaceValidator):
    TITLE = "Interface description *MUST NOT MATCH* regex"
    DESCRIPTION = """
        Interface description MUST NOT MATCH regular expression
    """
    TAGS = ["description"]
    CONFIG_FORM = [
        {
            "name": "regex",
            "xtype": "textfield",
            "fieldLabel": "REGEX",
            "allowBlank": False,
            "uiStyle": "extra"
        }
    ]
    RULES = """
    (defrule {{RULENAME}}
        (interface (name "{{name}}") (admin_status 1) (description ?d))
        (test (match-re "{{regex}}" ?d))
        =>
        (assert
            (error (type "Interface | Invalid Description")
                   (obj "{{name}}")
                   (msg "{{regex}}")
                   )
        )
    )
    """
