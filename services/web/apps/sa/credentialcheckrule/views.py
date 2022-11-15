# ---------------------------------------------------------------------
# sa.credentialcheckrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.sa.models.credentialcheckrule import CredentialCheckRule
from noc.core.translation import ugettext as _


class CredentialCheckRuleApplication(ExtDocApplication):
    """
    CredentialCheckRule application
    """

    title = _("Credential Check Rule")
    menu = [_("Setup"), _("Credential Check Rules")]
    model = CredentialCheckRule
    query_fields = ["name__icontains", "description__icontains"]
