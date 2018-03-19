# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ip.prefix application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from operator import attrgetter
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.ip.models.vrf import VRF
from noc.ip.models.prefix import Prefix
from noc.ip.models.prefixaccess import PrefixAccess
from noc.core.translation import ugettext as _
from noc.sa.interfaces.base import ModelParameter, PrefixParameter
from noc.core.ip import IP
from noc.lib.app.decorators.state import state_handler


@state_handler
class PrefixApplication(ExtModelApplication):
    """
    Prefix application
    """
    title = _("Prefix")
    model = Prefix

    def field_row_class(self, o):
        return o.profile.style.css_class_name if o.profile and o.profile.style else ""

    def can_create(self, user, obj):
        return PrefixAccess.user_can_change(user, obj.vrf, obj.afi, obj.prefix)

    def can_update(self, user, obj):
        return PrefixAccess.user_can_change(user, obj.vrf, obj.afi, obj.prefix)

    def can_delete(self, user, obj):
        return PrefixAccess.user_can_change(user, obj.vrf, obj.afi, obj.prefix)

    def queryset(self, request, query=None):
        qs = super(PrefixApplication, self).queryset(request, query=query)
        return qs.filter(PrefixAccess.read_Q(request.user))

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

    @view(
        url="^(?P<prefix_id>\d+)/suggest_free/$",
        method=["GET"], access="read", api=True
    )
    def api_suggest_free(self, request, prefix_id):
        """
        Suggest free blocks of different sizes
        :param request:
        :param prefix_id:
        :return:
        """
        prefix = self.get_object_or_404(Prefix, id=int(prefix_id))
        suggestions = []
        p_mask = int(prefix.prefix.split("/")[1])
        free = sorted(
            IP.prefix(prefix.prefix).iter_free([
                pp.prefix for pp in prefix.children_set.all()
            ]),
            key=attrgetter("mask"),
            reverse=True
        )
        # Find smallest free block possible
        for mask in range(30 if prefix.is_ipv4 else 64,
                          max(p_mask + 1, free[-1].mask) - 1, -1):
            # Find smallest free block possible
            for p in free:
                if p.mask <= mask:
                    suggestions += [{
                        "prefix": "%s/%d" % (p.address, mask),
                        "size": 2 ** (32 - mask) if prefix.is_ipv4 else None
                    }]
                    break
        return suggestions
