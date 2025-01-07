# ---------------------------------------------------------------------
# Peer model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import datetime
import logging
from typing import Optional

# Third-party modules
from django.db.models import (
    CharField,
    ForeignKey,
    IntegerField,
    DateTimeField,
    TextField,
    CASCADE,
    SET_NULL,
    BigIntegerField,
)
from django.contrib.postgres.fields import ArrayField

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.model.fields import INETField, DocumentReferenceField
from noc.core.mx import send_message, MessageType, MX_PROFILE_ID
from noc.core.model.decorator import on_save
from noc.core.gridvcs.manager import GridVCSField
from noc.core.wf.decorator import workflow
from noc.core.bgp import BGPState
from noc.project.models.project import Project
from noc.main.models.label import Label
from noc.wf.models.state import State
from noc.config import config
from .asn import AS
from .peerprofile import PeerProfile
from .peeringpoint import PeeringPoint

logger = logging.getLogger(__name__)


@Label.model
@workflow
@on_save
class Peer(NOCModel):
    """
    BGP Peering session
    """

    class Meta(object):
        verbose_name = "Peer"
        verbose_name_plural = "Peers"
        db_table = "peer_peer"
        app_label = "peer"

    profile: PeerProfile = ForeignKey(
        PeerProfile,
        verbose_name="Peer Profile",
        on_delete=CASCADE,
        default=PeerProfile.get_default_profile,
    )
    project = ForeignKey(
        Project,
        verbose_name="Project",
        null=True,
        blank=True,
        related_name="peer_set",
        on_delete=CASCADE,
    )
    managed_object = ForeignKey(
        "sa.ManagedObject",
        verbose_name="Managed Object",
        null=True,
        blank=True,
        on_delete=SET_NULL,
        help_text="Set if address belongs to the Managed Object's interface",
    )
    # Workflow
    state: "State" = DocumentReferenceField(State, null=True, blank=True)
    # Last state change
    state_changed = DateTimeField("State Changed", null=True, blank=True)
    # Timestamp expired
    expired = DateTimeField("Expired", null=True, blank=True)
    # Timestamp of last seen
    last_seen = DateTimeField("Last Seen", null=True, blank=True)
    # Timestamp of first discovery
    first_discovered = DateTimeField("First Discovered", null=True, blank=True)
    oper_status = IntegerField(
        choices=[
            (1, "idle"),
            (2, "connect"),
            (3, "active"),
            (4, "opensent"),
            (5, "openconfirm"),
            (6, "established"),
        ],
        null=True,
    )
    oper_status_change = DateTimeField("Oper Status Last Changed", null=True, blank=True)
    # RPSL Settings
    peering_point: Optional["PeeringPoint"] = ForeignKey(
        PeeringPoint, verbose_name="Peering Point", on_delete=CASCADE, null=True, blank=True
    )
    #
    local_asn: "AS" = ForeignKey(AS, verbose_name="Local AS", on_delete=CASCADE)
    local_ip = INETField("Local IP", null=True, blank=True)
    local_backup_ip = INETField("Local Backup IP", null=True, blank=True)
    remote_asn = BigIntegerField("Remote AS", null=True, blank=True)
    remote_ip = INETField("Remote IP")
    remote_backup_ip = INETField("Remote Backup IP", null=True, blank=True)
    import_filter = CharField("Import filter", max_length=64, default="any")
    # Override PeerProfile.local_pref
    local_pref: int = IntegerField("Local Pref", null=True, blank=True)
    # Override PeerProfile.import_med
    import_med: int = IntegerField("Import MED", blank=True, null=True)
    # Override PeerGroup.export_med
    export_med: int = IntegerField("Export MED", blank=True, null=True)
    export_filter = CharField("Export filter", max_length=64, default="any")
    description = TextField("Description", null=True, blank=True)
    # Peer remark to be shown in RPSL
    rpsl_remark = CharField("RPSL Remark", max_length=64, null=True, blank=True)
    tt = IntegerField("TT", blank=True, null=True)
    # In addition to PeerProfile.communities
    # and PeeringProfile.communities
    communities = CharField("Import Communities", max_length=128, blank=True, null=True)
    max_prefixes = IntegerField("Max. Prefixes", default=100)
    import_filter_name: Optional[str] = CharField(
        "Import Filter Name", max_length=64, blank=True, null=True
    )
    export_filter_name: Optional[str] = CharField(
        "Export Filter Name", max_length=64, blank=True, null=True
    )
    #
    labels = ArrayField(CharField(max_length=250), blank=True, null=True, default=list)
    effective_labels = ArrayField(CharField(max_length=250), blank=True, null=True, default=list)

    rpsl = GridVCSField("rpsl_peer")

    def __str__(self):
        if self.peering_point:
            return f" {self.remote_asn} ({self.remote_ip}@{self.peering_point.hostname})"
        return f" {self.remote_asn} ({self.remote_ip})"

    @property
    def name(self) -> str:
        return str(self)

    def save(self, *args, **kwargs):
        if self.import_filter_name is not None and not self.import_filter_name.strip():
            self.import_filter_name = None
        if self.export_filter_name is not None and not self.export_filter_name.strip():
            self.export_filter_name = None
        super().save(*args, **kwargs)
        if self.peering_point:
            self.touch_rpsl()

    @property
    def all_communities(self):
        r = {}
        for cl in [
            self.peering_point.communities,
            self.profile.get_data("communities"),
            self.communities,
        ]:
            if cl is None:
                continue
            for c in cl.replace(",", " ").split():
                r[c] = None
        c = sorted(r.keys())
        return " ".join(c)

    def get_rpsl(self):
        s = "import: from AS%d" % self.remote_asn
        s += " at %s" % self.peering_point.hostname
        actions = []
        local_pref = self.effective_local_pref
        if local_pref:
            # Select pref meaning
            if config.peer.rpsl_inverse_pref_style:
                pref = 65535 - local_pref  # RPSL style
            else:
                pref = local_pref
            actions += ["pref=%d;" % pref]
        import_med = self.effective_import_med
        if import_med:
            actions += ["med=%d;" % import_med]
        if actions:
            s += " action " + " ".join(actions)
        s += " accept %s\n" % self.import_filter
        actions = []
        export_med = self.effective_export_med
        if export_med:
            actions += ["med=%d;" % export_med]
        s += "export: to AS%s at %s" % (self.remote_asn, self.peering_point.hostname)
        if actions:
            s += " action " + " ".join(actions)
        s += " announce %s" % self.export_filter
        return s

    def get_effective_peer_data(self, name: str) -> Optional[str]:
        """Getting effective peer attribute by name"""

    @property
    def effective_max_prefixes(self) -> int:
        if self.max_prefixes:
            return self.max_prefixes
        if self.profile.max_prefixes:
            return self.profile.max_prefixes
        return 0

    @property
    def effective_local_pref(self) -> int:
        """Effective localpref: Peer specific or PeerGroup inherited"""
        if self.local_pref is not None:
            return self.local_pref
        return self.profile.get_data("local_pref")

    @property
    def effective_import_med(self):
        """Effective import med: Peer specific or PeerGroup inherited"""
        if self.import_med is not None:
            return self.import_med
        return self.profile.get_data("import_med")

    @property
    def effective_export_med(self):
        """Effective export med: Peer specific or PeerGroup inherited"""
        if self.export_med is not None:
            return self.export_med
        return self.profile.get_data("export_med")

    @classmethod
    def get_peer(cls, address: str) -> Optional["Peer"]:
        """
        Get peer by address
        Attrs:
            address: Remote address
        Return: Peer instance or None
        """
        data = list(
            Peer.objects.filter().extra(
                where=["host(remote_ip)=%s OR host(remote_backup_ip)=%s"], params=[address, address]
            )
        )
        if data:
            return data[0]
        return None

    @classmethod
    def get_component(cls, managed_object, peer=None, **kwargs) -> Optional["Peer"]:
        if peer:
            return Peer.get_peer(peer)

    def touch_rpsl(self):
        c_rpsl = self.rpsl.read()
        n_rpsl = self.get_rpsl()
        if c_rpsl == n_rpsl:
            return  # Not changed
        self.rpsl.write(n_rpsl)

    def on_save(self):
        if self.peering_point:
            self.touch_rpsl()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_peer")

    def get_partner_object(self):
        """Search ManagedObject by Remote asn"""
        from noc.sa.models.managedobject import ManagedObject
        from noc.inv.models.subinterface import SubInterface

        mo = ManagedObject.objects.filter(address=self.remote_ip).first()
        if mo:
            return mo
        si = SubInterface.objects.filter(ipv4_addresses=re.compile(str(self.remote_ip)))
        if si:
            return si.managed_object

    def set_oper_status(self, status: BGPState, timestamp: Optional[datetime.datetime] = None):
        """
        Set Operational Status for Service
        Args:
            status: New status
            timestamp: Time when status changed
        """
        # Check state on is_productive
        # if not self.state.is_productive:
        #    return
        current = BGPState(self.oper_status) if self.oper_status else None
        if current == status:
            logger.debug("[%s] Status is same. Skipping", self.id)
            return
        now = datetime.datetime.now().replace(microsecond=0)
        logger.info(
            "[%s] Change Peer status: %s -> %s",
            self.id,
            current,
            status,
        )
        timestamp = timestamp or now
        if self.oper_status_change and self.oper_status_change > timestamp:
            return
        Peer.objects.filter(id=self.id).update(
            oper_status=status.value, oper_status_change=timestamp
        )
        if self.profile.is_enabled_notification and self.oper_status is not None:
            logger.debug("Sending status change notification")
            headers = {}
            data = {}
            if self.managed_object:
                headers |= self.managed_object.get_mx_message_headers(self.effective_labels)
                data["managed_object"] = self.managed_object.get_message_context()
            # if self.profile.default_notification_group:
            #     headers[MX_NOTIFICATION_GROUP_ID] = str(
            #         self.profile.default_notification_group.id
            #     ).encode()
            headers[MX_PROFILE_ID] = str(self.profile.id).encode()
            send_message(
                data={
                    "name": self.name,
                    "description": self.description,
                    "local_as": self.local_asn.get_message_context(),
                    "local_ip": self.local_ip,
                    "remote_asn": self.remote_asn,
                    "remote_ip": self.remote_ip,
                    "profile": {"id": str(self.profile.id), "name": self.profile.name},
                    "status": status,
                    "from_status": current,
                },
                message_type=MessageType.PEER_STATUS_CHANGE,
                headers=headers,
            )
