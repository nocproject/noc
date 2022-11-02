# ---------------------------------------------------------------------
# Interactive prefix list builder
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extapplication import ExtApplication, view
from noc.peer.models.peeringpoint import PeeringPoint
from noc.peer.models.whoiscache import WhoisCache
from noc.sa.interfaces.base import UnicodeParameter, ModelParameter
from noc.core.translation import ugettext as _

# as_set_re = "^AS(?:\d+|-\S+)(:\S+)?(?:\s+AS(?:\d+|-\S+)(:\S+)?)*$"


class PrefixListBuilderApplication(ExtApplication):
    """
    Interactive prefix list builder
    """

    title = _("Prefix List Builder")
    menu = _("Prefix List Builder")

    @view(
        method=["GET"],
        url=r"^$",
        access="read",
        api=True,
        validate={
            "peering_point": ModelParameter(PeeringPoint),
            "name": UnicodeParameter(required=False),
            "as_set": UnicodeParameter(),
        },
    )
    def api_list(self, request, peering_point, name, as_set):
        if not WhoisCache.has_asset_members():
            return {
                "name": name,
                "prefix_list": "",
                "success": False,
                "message": _("AS-SET members cache is empty. Please update Whois Cache"),
            }
        if not WhoisCache.has_origin_routes():
            return {
                "name": name,
                "prefix_list": "",
                "success": False,
                "message": _("Origin routes cache is empty. Please update Whois Cache"),
            }
        if not WhoisCache.has_asset(as_set):
            return {
                "name": name,
                "prefix_list": "",
                "success": False,
                "message": _("Unknown AS-SET"),
            }
        prefixes = WhoisCache.resolve_as_set_prefixes_maxlen(as_set)
        if not prefixes:
            return {
                "name": name,
                "prefix_list": "",
                "success": False,
                "message": _("Cannot resolve AS-SET prefixes"),
            }
        try:
            pl = peering_point.profile.get_profile().generate_prefix_list(name, prefixes)
        except NotImplementedError:
            return {
                "name": name,
                "prefix_list": "",
                "success": False,
                "message": _("Prefix-list generator is not implemented for this profile"),
            }
        return {"name": name, "prefix_list": pl, "success": True, "message": _("Prefix List built")}
