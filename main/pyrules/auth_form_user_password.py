# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Returns authentication form class for user/password validation
##----------------------------------------------------------------------
## INTERFACE: IAuthenticationForm
##----------------------------------------------------------------------
## DESCRIPTION:
## Returns authentication form class for user/password validation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

@pyrule
def auth_form_user_password():
    return [
        {
            "xtype": "textfield",
            "name": "username",
            "fieldLabel": "Name",
            "allowBlank": False,
            "emptyText": "Enter username"
        },

        {
            "xtype": "textfield",
            "name": "password",
            "fieldLabel": "Password",
            "allowBlank": False,
            "inputType": "password"
        }
    ]
