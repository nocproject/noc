# ---------------------------------------------------------------------
# ObjectNotify Manager
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication
from noc.cm.models.objectnotify import ObjectNotify
from noc.core.translation import ugettext as _


class ObjectNotifyApplication(ExtModelApplication):
    title = _("Object Notifies")
    menu = [_("Setup"), _("Object Notifies")]
    glyph = "flag-o"
    model = ObjectNotify
