# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.authldapdomain application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app import ExtDocApplication
from noc.main.models.authldapdomain import AuthLDAPDomain


class AuthLDAPDomainApplication(ExtDocApplication):
    """
    AuthLDAPDomain application
    """
    title = "LDAP Domain"
    menu = [_("Setup"), _("LDAP Domains")]
    model = AuthLDAPDomain
