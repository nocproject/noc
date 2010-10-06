# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Returns authentication form class for user/password validation
##----------------------------------------------------------------------
## INTERFACE: IAuthenticationForm
##----------------------------------------------------------------------
## DESCRIPTION:
## Returns authentication form class for user/password validation
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.forms import NOCAuthenticationForm
from django import forms

class NOCUserPasswordAuthenticationForm(NOCAuthenticationForm):
    username = forms.CharField(label="Username", max_length=30)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

@pyrule
def auth_form_user_password():
    return NOCUserPasswordAuthenticationForm
