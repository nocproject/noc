# ---------------------------------------------------------------------
# AS model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional
import operator

# Third-party modules
from django.db import models
from django.contrib.postgres.fields import ArrayField
import cachetools

# NOC modules
from noc.core.model.base import NOCModel
from noc.project.models.project import Project
from noc.main.models.label import Label
from noc.config import config
from noc.core.rpsl import rpsl_format
from noc.core.model.decorator import on_delete_check, on_save
from noc.core.gridvcs.manager import GridVCSField
from noc.core.model.fields import DocumentReferenceField
from .person import Person
from .organisation import Organisation
from .maintainer import Maintainer
from .rir import RIR
from .asprofile import ASProfile

id_lock = Lock()


@Label.model
@on_delete_check(
    check=[("peer.Peer", "local_asn"), ("peer.PeeringPoint", "local_as"), ("ip.Prefix", "asn")]
)
@on_save
class AS(NOCModel):
    class Meta(object):
        verbose_name = "AS"
        verbose_name_plural = "ASes"
        db_table = "peer_as"
        app_label = "peer"

    asn = models.BigIntegerField("ASN", unique=True)
    # as-name RPSL Field
    as_name = models.CharField("AS Name", max_length=64, null=True, blank=True)
    profile = DocumentReferenceField(ASProfile, null=False, blank=False)
    project = models.ForeignKey(
        Project,
        verbose_name="Project",
        null=True,
        blank=True,
        related_name="as_set",
        on_delete=models.CASCADE,
    )
    # RPSL descr field
    description = models.TextField("Description")
    organisation = models.ForeignKey(
        Organisation, verbose_name="Organisation", on_delete=models.CASCADE
    )
    administrative_contacts = models.ManyToManyField(
        Person,
        verbose_name="admin-c",
        related_name="as_administrative_contacts",
        null=True,
        blank=True,
    )
    tech_contacts = models.ManyToManyField(
        Person, verbose_name="tech-c", related_name="as_tech_contacts", null=True, blank=True
    )
    maintainers = models.ManyToManyField(
        Maintainer, verbose_name="Maintainers", related_name="as_maintainers", null=True, blank=True
    )
    routes_maintainers = models.ManyToManyField(
        Maintainer,
        verbose_name="Routes Maintainers",
        related_name="as_route_maintainers",
        null=True,
        blank=True,
    )
    # remarks: will be prepended automatically
    header_remarks = models.TextField("Header Remarks", null=True, blank=True)
    # remarks: will be prepended automatically
    footer_remarks = models.TextField("Footer Remarks", null=True, blank=True)
    rir = models.ForeignKey(RIR, verbose_name="RIR", on_delete=models.CASCADE)
    #
    labels = ArrayField(models.CharField(max_length=250), blank=True, null=True, default=list)
    effective_labels = ArrayField(
        models.CharField(max_length=250), blank=True, null=True, default=list
    )
    rpsl = GridVCSField("rpsl_as")

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _asn_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return "AS%d (%s)" % (self.asn, self.description)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id: int) -> Optional["AS"]:
        asn = AS.objects.filter(id=id)[:1]
        if asn:
            return asn[0]
        return None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_asn_cache"), lock=lambda _: id_lock)
    def get_by_asn(cls, asn):
        asn = AS.objects.filter(asn=asn)[:1]
        if asn:
            return asn[0]
        return None

    def get_rpsl(self):
        sep = "remarks: %s" % ("-" * 72)
        s = []
        s += ["aut-num: AS%s" % self.asn]
        if self.as_name:
            s += ["as-name: %s" % self.as_name]
        if self.description:
            s += ["descr: %s" % x for x in self.description.split("\n")]
        s += ["org: %s" % self.organisation.organisation]
        # Add header remarks
        if self.header_remarks:
            s += ["remarks: %s" % x for x in self.header_remarks.split("\n")]
        # Find AS peers
        pg = (
            {}
        )  # Peer Group -> AS -> peering_point -> [(import, export, localpref, import_med, export_med, remark)]
        for peer in self.peer_set.filter(status="A"):
            if peer.peer_group not in pg:
                pg[peer.peer_group] = {}
            if peer.remote_asn not in pg[peer.peer_group]:
                pg[peer.peer_group][peer.remote_asn] = {}
            if peer.peering_point not in pg[peer.peer_group][peer.remote_asn]:
                pg[peer.peer_group][peer.remote_asn][peer.peering_point] = []
            to_skip = False
            e_import_med = peer.effective_import_med
            e_export_med = peer.effective_export_med
            for R in pg[peer.peer_group][peer.remote_asn][peer.peering_point]:
                p_import, p_export, localpref, import_med, export_med, remark = R
                if (
                    peer.import_filter == p_import
                    and peer.export_filter == p_export
                    and e_import_med == import_med
                    and e_export_med == export_med
                ):
                    to_skip = True
                    break
            if not to_skip:
                pg[peer.peer_group][peer.remote_asn][peer.peering_point] += [
                    (
                        peer.import_filter,
                        peer.export_filter,
                        peer.effective_local_pref,
                        e_import_med,
                        e_export_med,
                        peer.rpsl_remark,
                    )
                ]
        # Build RPSL
        inverse_pref = config.peer.rpsl_inverse_pref_style
        for peer_group in pg:
            s += [sep]
            s += ["remarks: -- %s" % x for x in peer_group.description.split("\n")]
            s += [sep]
            for asn in sorted(pg[peer_group]):
                add_at = len(pg[peer_group][asn]) != 1
                for pp in pg[peer_group][asn]:
                    for R in pg[peer_group][asn][pp]:
                        import_filter, export_filter, localpref, import_med, export_med, remark = R
                        # Prepend import and export with remark when given
                        if remark:
                            s += ["remarks: # %s" % remark]
                        # Build import statement
                        i_s = "import: from AS%d" % asn
                        if add_at:
                            i_s += " at %s" % pp.hostname
                        actions = []
                        if localpref:
                            pref = (65535 - localpref) if inverse_pref else localpref
                            actions += ["pref=%d;" % pref]
                        if import_med:
                            actions += ["med=%d;" % import_med]
                        if actions:
                            i_s += " action " + " ".join(actions)
                        i_s += " accept %s" % import_filter
                        s += [i_s]
                        # Build export statement
                        e_s = "export: to AS%d" % asn
                        if add_at:
                            e_s += " at %s" % pp.hostname
                        if export_med:
                            e_s += " action med=%d;" % export_med
                        e_s += " announce %s" % export_filter
                        s += [e_s]
        # Add contacts
        for c in self.administrative_contacts.order_by("nic_hdl"):
            s += ["admin-c: %s" % c.nic_hdl]
        for c in self.tech_contacts.order_by("nic_hdl"):
            s += ["tech-c: %s" % c.nic_hdl]
        # Add maintainers
        for m in self.maintainers.all():
            s += ["mnt-by: %s" % m.maintainer]
        for m in self.routes_maintainers.all():
            s += ["mnt-routes: %s" % m.maintainer]
        # Add footer remarks
        if self.footer_remarks:
            s += ["remarks: %s" % x for x in self.footer_remarks.split("\n")]
        return rpsl_format("\n".join(s))

    def touch_rpsl(self):
        c_rpsl = self.rpsl.read()
        n_rpsl = self.get_rpsl()
        if c_rpsl == n_rpsl:
            return  # Not changed
        self.rpsl.write(n_rpsl)

    def on_save(self):
        self.touch_rpsl()

    @property
    def dot(self):
        from .peer import Peer

        s = ["graph {"]
        all_peers = Peer.objects.filter(local_asn__exact=self)
        uplinks = {}
        peers = {}
        downlinks = {}
        for p in all_peers:
            if p.import_filter == "ANY" and p.export_filter != "ANY":
                uplinks[p.remote_asn] = p
            elif p.export_filter == "ANY":
                downlinks[p.remote_asn] = p
            else:
                peers[p.remote_asn] = p
        asn = "AS%d" % self.asn
        for subgraph, peers in [
            ("uplinks", list(uplinks.values())),
            ("peers", list(peers.values())),
            ("downlinks", list(downlinks.values())),
        ]:
            s += ["subgraph %s {" % subgraph]
            for p in peers:
                attrs = ['taillabel=" %s"' % p.import_filter, 'headlabel=" %s"' % p.export_filter]
                if p.import_filter == "ANY":
                    attrs += ["arrowtail=open"]
                if p.export_filter == "ANY":
                    attrs += ["arrothead=open"]
                s += ["    %s -- AS%d [%s];" % (asn, p.remote_asn, ",".join(attrs))]
            s += ["}"]
        s += ["}"]
        return "\n".join(s)

    def update_rir_db(self):
        return self.rir.update_rir_db(self.rpsl, self.maintainers.all()[0])

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_asn")
