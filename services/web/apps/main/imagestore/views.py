# ---------------------------------------------------------------------
# Image Store
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.main.models.imagestore import ImageStore
from noc.core.translation import ugettext as _


class ImageStoreApplication(ExtModelApplication):
    title = _("Images")
    model = ImageStore
    menu = [_("Setup"), _("Images")]
    query_fields = ["name__icontains"]
