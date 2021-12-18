# ---------------------------------------------------------------------
# vc.vlanfilter application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.vc.models.vlanfilter import VLANFilter
from noc.sa.interfaces.base import IntParameter
from noc.core.translation import ugettext as _


class VLANFilterApplication(ExtDocApplication):
    """
    VLANFilter application
    """

    title = _("VLAN Filter")
    menu = [_("Setup"), _("VLAN Filters")]
    model = VLANFilter

    def lookup_vc(self, q, name, value):
        """
        Resolve __vc lookups
        :param q:
        :param name:
        :param value:
        :return:
        """
        value = IntParameter().clean(value)
        filters = [str(f.id) for f in VLANFilter.objects.filters(include_vlans__in=[value])]
        if filters:
            x = "(id IN (%s))" % ", ".join(filters)
        else:
            x = "FALSE"
        try:
            q[None] += [x]
        except KeyError:
            q[None] = [x]
