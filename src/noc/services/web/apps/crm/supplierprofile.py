# ---------------------------------------------------------------------
# crm.supplierprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.crm.models.supplierprofile import SupplierProfile
from noc.services.web.base.extdocapplication import ExtDocApplication


class SupplierProfileApplication(ExtDocApplication):
    """
    SupplierProfile application
    """

    title = _("Supplier Profile")
    menu = [_("Setup"), _("Supplier Profiles")]
    model = SupplierProfile
    query_fields = ["name__icontains", "description__icontains"]
