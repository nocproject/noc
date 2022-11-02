# ----------------------------------------------------------------------
# main.extstorage application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extdocapplication import ExtDocApplication
from noc.main.models.extstorage import ExtStorage
from noc.core.translation import ugettext as _


class ExtStorageApplication(ExtDocApplication):
    """
    ExtStorage application
    """

    title = _("Ext. Storage")
    menu = [_("Setup"), _("Ext. Storages")]
    model = ExtStorage
    glyph = "database"
