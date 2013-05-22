# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PeeringPoint model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## NOC modules
from noc.main.models import NotificationGroup
from asn import AS
from noc.sa.models import profile_registry
from noc.lib.rpsl import rpsl_format


class PeeringPoint(models.Model):
    class Meta:
        verbose_name = "Peering Point"
        verbose_name_plural = "Peering Points"
        db_table = "peer_peeringpoint"
        app_label = "peer"

    # @todo: Replace with managed object
    hostname = models.CharField("FQDN", max_length=64, unique=True)
    location = models.CharField(
        "Location", max_length=64, blank=True, null=True)
    local_as = models.ForeignKey(AS, verbose_name="Local AS")
    router_id = models.IPAddressField("Router-ID", unique=True)
    # @todo: Replace with managed object
    profile_name = models.CharField("Profile", max_length=128,
                                    choices=profile_registry.choices)
    communities = models.CharField(
        "Import Communities", max_length=128,
        blank=True, null=True)
    enable_prefix_list_provisioning = models.BooleanField(
        "Enable Prefix-List Provisioning", default=False)
    prefix_list_notification_group = models.ForeignKey(
        NotificationGroup,
        verbose_name="Prefix List Notification Group",
        null=True, blank=True)

    def __unicode__(self):
        if self.location:
            return u" %s (%s)" % (self.hostname, self.location)
        else:
            return self.hostname

    def sync_cm_prefix_list(self):
        from noc.cm.models import PrefixList
        peers_pl = set()
        peers_pl.update([p.import_filter_name for p in self.peer_set.filter(import_filter_name__isnull=False) if p.import_filter_name.strip()])
        peers_pl.update([p.export_filter_name for p in self.peer_set.filter(export_filter_name__isnull=False) if p.export_filter_name.strip()])
        h = self.hostname + "/"
        l_h = len(h)
        for p in PrefixList.objects.filter(repo_path__startswith=h):
            pl = p.path[l_h:]
            if pl not in peers_pl:
                p.delete()
            else:
                del peers_pl[pl]
        for pl in peers_pl:
            PrefixList(repo_path=h + pl).save()

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
        return pls.items()

    @property
    def profile(self):
        return profile_registry[self.profile_name]()

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
        for remote_ip, remote_as in sorted(peers.keys(), key=lambda x: x[0]):
            if "/" in remote_ip:
                remote_ip, masklen = remote_ip.split("/")
            s += ["peer: BGP4 %s asno(%s)" % (remote_ip, remote_as)]
        return rpsl_format("\n".join(s))
