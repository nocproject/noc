# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ip.prefix application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.ip.models.vrf import VRF
from noc.ip.models.prefix import Prefix
from noc.core.translation import ugettext as _
from noc.sa.interfaces.base import ModelParameter, PrefixParameter


class PrefixApplication(ExtModelApplication):
    """
    Prefix application
    """
    title = _("Prefix")
    menu = [_("Setup"), _("Prefix")]
    model = Prefix

    def field_row_class(self, o):
        return o.profile.style.css_class_name if o.profile and o.profile.style else ""

    @view(
        url="^(?P<prefix_id>\d+)/rebase/$",
        method=["POST"], access="rebase", api=True,
        validate={
            "to_vrf": ModelParameter(VRF),
            "to_prefix": PrefixParameter()
        }
    )
    def api_rebase(self, request, prefix_id, to_vrf, to_prefix):
        prefix = self.get_object_or_404(Prefix, id=int(prefix_id))
        try:
            new_prefix = prefix.rebase(to_vrf, to_prefix)
            return self.instance_to_dict(new_prefix)
        except ValueError as e:
            return self.response_bad_request(str(e))
