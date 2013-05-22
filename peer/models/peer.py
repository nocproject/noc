# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Peer model
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Peer modules
from noc.project.models.project import Project
from asn import AS
from peergroup import PeerGroup
from peeringpoint import PeeringPoint
from noc.lib.fields import INETField, TagsField
from noc.lib.tt import tt_url
from noc.settings import config
from noc.lib.app.site import site


class Peer(models.Model):
    """
    BGP Peering session
    """
    class Meta:
        verbose_name = "Peer"
        verbose_name_plural = "Peers"
        db_table = "peer_peer"
        app_label = "peer"

    peer_group = models.ForeignKey(
        PeerGroup, verbose_name="Peer Group")
    project = models.ForeignKey(
        Project, verbose_name="Project",
        null=True, blank=True, related_name="peer_set")
    peering_point = models.ForeignKey(
        PeeringPoint, verbose_name="Peering Point")
    local_asn = models.ForeignKey(AS, verbose_name="Local AS")
    local_ip = INETField("Local IP")
    local_backup_ip = INETField(
        "Local Backup IP", null=True, blank=True)
    remote_asn = models.IntegerField("Remote AS")
    remote_ip = INETField("Remote IP")
    remote_backup_ip = INETField(
        "Remote Backup IP", null=True, blank=True)
    status = models.CharField("Status", max_length=1, default="A",
                              choices=[("P", "Planned"),
                                       ("A", "Active"),
                                       ("S", "Shutdown")])
    import_filter = models.CharField("Import filter", max_length=64)
    # Override PeerGroup.local_pref
    local_pref = models.IntegerField(
        "Local Pref", null=True, blank=True)
    # Override PeerGroup.import_med
    import_med = models.IntegerField(
        "Import MED", blank=True, null=True)
    # Override PeerGroup.export_med
    export_med = models.IntegerField(
        "Export MED", blank=True, null=True)
    export_filter = models.CharField("Export filter", max_length=64)
    description = models.CharField("Description", max_length=64,
                                   null=True, blank=True)
    # Peer remark to be shown in RPSL
    rpsl_remark = models.CharField("RPSL Remark", max_length=64,
                                   null=True, blank=True)
    tt = models.IntegerField("TT", blank=True, null=True)
    # In addition to PeerGroup.communities
    #and PeeringPoint.communities
    communities = models.CharField("Import Communities", max_length=128,
                                   blank=True, null=True)
    max_prefixes = models.IntegerField("Max. Prefixes", default=100)
    import_filter_name = models.CharField(
        "Import Filter Name", max_length=64, blank=True, null=True)
    export_filter_name = models.CharField(
        "Export Filter Name", max_length=64, blank=True, null=True)
    tags = TagsField("Tags", null=True, blank=True)

    def __unicode__(self):
        return u" %s (%s@%s)" % (self.remote_asn, self.remote_ip,
                                 self.peering_point.hostname)

    def get_absolute_url(self):
        return site.reverse("peer:peer:change", self.id)

    def save(self):
        if (self.import_filter_name is not None and
                not self.import_filter_name.strip()):
            self.import_filter_name = None
        if (self.export_filter_name is not None and
                not self.export_filter_name.strip()):
            self.export_filter_name = None
        super(Peer, self).save()
        self.peering_point.sync_cm_prefix_list()

    @property
    def tt_url(self):
        return tt_url(self)

    @property
    def all_communities(self):
        r = {}
        for cl in [self.peering_point.communities,
                   self.peer_group.communities,
                   self.communities]:
            if cl is None:
                continue
            for c in cl.replace(",", " ").split():
                r[c] = None
        c = sorted(r.keys())
        return " ".join(c)

    @property
    def rpsl(self):
        s = "import: from AS%d" % self.remote_asn
        s += " at %s" % self.peering_point.hostname
        actions = []
        local_pref = self.effective_local_pref
        if local_pref:
            # Select pref meaning
            if config.getboolean("peer", "rpsl_inverse_pref_style"):
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
        s += "export: to AS%s at %s" % (self.remote_asn,
                                       self.peering_point.hostname)
        if actions:
            s += " action " + " ".join(actions)
        s += " announce %s" % self.export_filter
        return s

    @property
    def effective_max_prefixes(self):
        if self.max_prefixes:
            return self.max_prefixes
        if self.peer_group.max_prefixes:
            return self.peer_group.max_prefixes
        return 0

    @property
    def effective_local_pref(self):
        """
        Effective localpref: Peer specific or PeerGroup inherited
        """
        if self.local_pref is not None:
            return self.local_pref
        return self.peer_group.local_pref

    @property
    def effective_import_med(self):
        """
        Effective import med: Peer specific or PeerGroup inherited
        """
        if self.import_med is not None:
            return self.import_med
        return self.peer_group.import_med

    @property
    def effective_export_med(self):
        """
        Effective export med: Peer specific or PeerGroup inherited
        """
        if self.export_med is not None:
            return self.export_med
        return self.peer_group.export_med

    @classmethod
    def get_peer(cls, address):
        """
        Get peer by address

        :param address: Remote address
        :type address: Str
        :returns: Peer instance or None
        """
        try:
            data = list(Peer.object.filter().extra(
                where=[
                    "host(remote_ip)=% OR host(remote_backup_ip)=%s"
                ],
                params=[address, address]
            ))
            return data[0]
        except Peer.DoesNotExist:
            return None
