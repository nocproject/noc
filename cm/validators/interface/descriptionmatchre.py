# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface description *MUST MATCH* regexp
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.cm.validators.clipsinterface import CLIPSInterfaceValidator


class InterfaceDescriptionMatchRegexpValidator(CLIPSInterfaceValidator):
    TITLE = "Interface description *MUST MATCH* regex"
    DESCRIPTION = """
        Interface description MUST MATCH regular expression
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
        (test (not (match-re "{{regex}}" ?d)))
        =>
        (assert
            (error (type "Interface | Invalid Description")
                   (obj "{{name}}")
                   (msg "{{regex}}")
                   )
        )
    )
    """
