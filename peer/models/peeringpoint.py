# ---------------------------------------------------------------------
# PeeringPoint model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from noc.main.models.notificationgroup import NotificationGroup
from noc.sa.models.profile import Profile
from noc.core.model.fields import DocumentReferenceField
from noc.core.rpsl import rpsl_format
from noc.core.model.decorator import on_delete_check
from .asn import AS


@on_delete_check(check=[("peer.Peer", "peering_point"), ("peer.PrefixListCache", "peering_point")])
class PeeringPoint(NOCModel):
    class Meta(object):
        verbose_name = "Peering Point"
        verbose_name_plural = "Peering Points"
        db_table = "peer_peeringpoint"
        app_label = "peer"

    # @todo: Replace with managed object
    hostname = models.CharField("FQDN", max_length=64, unique=True)
    location = models.CharField("Location", max_length=64, blank=True, null=True)
    local_as = models.ForeignKey(AS, verbose_name="Local AS", on_delete=models.CASCADE)
    router_id = models.GenericIPAddressField("Router-ID", unique=True, protocol="IPv4")
    # @todo: Replace with managed object
    profile = DocumentReferenceField(Profile, null=False, blank=False)
    communities = models.CharField("Import Communities", max_length=128, blank=True, null=True)
    enable_prefix_list_provisioning = models.BooleanField(
        "Enable Prefix-List Provisioning", default=False
    )
    prefix_list_notification_group = models.ForeignKey(
        NotificationGroup,
        verbose_name="Prefix List Notification Group",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        if self.location:
            return " %s (%s)" % (self.hostname, self.location)
        return self.hostname

    @property
    def generated_prefix_lists(self):
        """
        Returns a list of (prefix-list-name, rpsl-filter)
        """
        pls = {}
        for pr in self.peer_set.all():
            if pr.import_filter_name:
                pls[pr.import_filter_name] = pr.import_filter
            if pr.export_filter_name:
                pls[pr.export_filter_name] = pr.export_filter
        return list(pls.items())

    @property
    def rpsl(self):
        ifaddrs = set()
        peers = {}
        for p in self.peer_set.all():
            ifaddrs.add(p.local_ip)
            peers[p.remote_ip, p.remote_asn] = None
            if p.local_backup_ip and p.remote_backup_ip:
                ifaddrs.add(p.local_backup_ip)
                peers[p.remote_backup_ip, p.remote_asn] = None
        s = []
        s += ["inet-rtr: %s" % self.hostname]
        s += ["local-as: AS%d" % self.local_as.asn]
        for ip in sorted(ifaddrs):
            if "/" in ip:
                ip, masklen = ip.split("/")
            else:
                masklen = "30"
            s += ["ifaddr: %s masklen %s" % (ip, masklen)]
        for remote_ip, remote_as in sorted(peers, key=lambda x: x[0]):
            if "/" in remote_ip:
                remote_ip, masklen = remote_ip.split("/")
            s += ["peer: BGP4 %s asno(%s)" % (remote_ip, remote_as)]
        return rpsl_format("\n".join(s))
