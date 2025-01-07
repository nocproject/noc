# ---------------------------------------------------------------------
# peer.peer application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication, view
from noc.services.web.base.decorators.state import state_handler
from noc.peer.models.peer import Peer
from noc.core.validators import is_prefix
from noc.core.ip import IP
from noc.services.web.base.repoinline import RepoInline
from noc.sa.interfaces.base import ListOfParameter, ModelParameter
from noc.core.translation import ugettext as _


@state_handler
class PeerApplication(ExtModelApplication):
    """
    Peers application
    """

    title = _("Peers")
    menu = _("Peers")
    model = Peer
    query_fields = [
        "remote_asn__icontains",
        "description__icontains",
        "local_ip__icontains",
        "local_backup_ip__icontains",
        "remote_ip__icontains",
        "remote_backup_ip__icontains",
    ]
    rpsl = RepoInline("rpsl")

    def instance_to_dict(self, o, fields=None):
        data = super().instance_to_dict(o, fields=fields)
        # Expand resource groups fields
        if isinstance(o, Peer):
            data["in_maintenance"] = False
        return data

    def clean(self, data):
        data = super().clean(data)
        # Check address fields
        if not is_prefix(data["local_ip"]):
            raise ValueError("Invalid 'Local IP Address', must be in x.x.x.x/x form or IPv6 prefix")
        if not is_prefix(data["remote_ip"]):
            raise ValueError(
                "Invalid 'Remote IP Address', must be in x.x.x.x/x form or IPv6 prefix"
            )
        if "local_backup_ip" in data and data["local_backup_ip"]:
            if not is_prefix(data["local_backup_ip"]):
                raise ValueError(
                    "Invalid 'Local Backup IP Address', must be in x.x.x.x/x form or IPv6 prefix"
                )
        if "remote_backup_ip" in data and data["remote_backup_ip"]:
            if not is_prefix(data["remote_backup_ip"]):
                raise ValueError(
                    "Invalid 'Remote Backup IP Address', must be in x.x.x.x/x form or IPv6 prefix"
                )

        # Check no or both backup addresses given
        has_local_backup = "local_backup_ip" in data and data["local_backup_ip"]
        has_remote_backup = "remote_backup_ip" in data and data["remote_backup_ip"]
        if has_local_backup and not has_remote_backup:
            raise ValueError("One of backup addresses given. Set peer address")
        if not has_local_backup and has_remote_backup:
            raise ValueError("One of backup addresses given. Set peer address")
        # Check all link addresses belongs to one AFI
        if (
            len(
                {
                    IP.prefix(data[x]).afi
                    for x in ["local_ip", "remote_ip", "local_backup_ip", "remote_backup_ip"]
                    if x in data and data[x]
                }
            )
            > 1
        ):
            raise ValueError("All neighboring addresses must have same address family")
        return data

    def set_peer_status(self, request, queryset, event, message):
        """
        Change peer status
        :param request:
        :param queryset:
        :param status:
        :param message:
        :return:
        """
        count = 0
        for p in queryset:
            p.fire_event(event)
            count += 1
        if count == 1:
            return f"1 peer marked as {message}"
        return f"{count} peers marked as {message}"

    @view(
        url="^actions/planned/$",
        method=["POST"],
        access="update",
        api=True,
        validate={"ids": ListOfParameter(element=ModelParameter(Peer))},
    )
    def api_action_planned(self, request, ids):
        return self.set_peer_status(request, ids, "planned", "planned")

    api_action_planned.short_description = "Mark as planned"

    @view(
        url="^actions/active/$",
        method=["POST"],
        access="update",
        api=True,
        validate={"ids": ListOfParameter(element=ModelParameter(Peer))},
    )
    def api_action_active(self, request, ids):
        return self.set_peer_status(request, ids, "up", "active")

    api_action_active.short_description = "Mark as active"

    @view(
        url="^actions/shutdown/$",
        method=["POST"],
        access="update",
        api=True,
        validate={"ids": ListOfParameter(element=ModelParameter(Peer))},
    )
    def api_action_shutdown(self, request, ids):
        return self.set_peer_status(request, ids, "down", "shutdown")

    api_action_shutdown.short_description = "Mark as shutdown"
