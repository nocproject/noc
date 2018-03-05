# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.authldapdomain application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.main.models.authldapdomain import AuthLDAPDomain
from noc.core.translation import ugettext as _


class AuthLDAPDomainApplication(ExtDocApplication):
    """
    AuthLDAPDomain application
    """
    title = "LDAP Domain"
    menu = [_("Setup"), _("LDAP Domains")]
    model = AuthLDAPDomain
