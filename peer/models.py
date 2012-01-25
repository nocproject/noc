# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Peer module models
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import random
import time
import logging
import urllib
import urllib2
## Django modules
from django.db import models, connection
## NOC modules
from noc.settings import config
from noc.lib.validators import check_asn, check_as_set, is_ipv4,\
                               is_cidr, is_asn
from noc.lib.tt import tt_url
from noc.lib.rpsl import rpsl_format
from noc.lib.fields import INETField, InetArrayField, AutoCompleteTagsField
from noc.sa.profiles import profile_registry
from noc.main.models import NotificationGroup
from noc.cm.models import PrefixList
from noc.sa.models import AdministrativeDomain
from noc.lib.middleware import get_user
from noc.lib.crypto import md5crypt
from noc.lib.app.site import site
from noc.peer.tree import optimize_prefix_list, optimize_prefix_list_maxlen
from noc.lib import nosql


##
## Exception classes
##
class RIRDBUpdateError(Exception):
    pass
##
try:
    import ssl
    # Use SSL-enabled version when possible
    RIPE_SYNCUPDATES_URL = "https://syncupdates.db.ripe.net"
except ImportError:
    RIPE_SYNCUPDATES_URL = "http://syncupdates.db.ripe.net"


class RIR(models.Model):
    """
    Regional internet registries
    """
    class Meta:
        verbose_name = "RIR"
        verbose_name_plural = "RIRs"
        ordering = ["name"]

    name = models.CharField("name", max_length=64, unique=True)
    whois = models.CharField("whois", max_length=64, blank=True, null=True)

    def __unicode__(self):
        return self.name

    # Update RIR's database API and returns report
    def update_rir_db(self, data, maintainer=None):
        rir = "RIPE" if self.name == "RIPE NCC" else self.name
        return getattr(self, "update_rir_db_%s" % rir)(data, maintainer)

    # RIPE NCC Update API
    def update_rir_db_RIPE(self, data, maintainer):
        data = [x for x in data.split("\n") if x]  # Strip empty lines
        if maintainer.password:
            data += ["password: %s" % maintainer.password]
        admin = maintainer.admins.all()[0]
        T = time.gmtime()
        data += ["changed: %s %04d%02d%02d" % (admin.email, T[0], T[1], T[2])]
        data += ["source: RIPE"]
        data = "\n".join(data)
        try:
            f = urllib2.urlopen(url=RIPE_SYNCUPDATES_URL,
                                data=urllib.urlencode({"DATA": data}))
            data = f.read()
        except urllib2.URLError, why:
            data = "Update failed: %s" % why
        return data


class Person(models.Model):
    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "Persons"

    nic_hdl = models.CharField("nic-hdl", max_length=64, unique=True)
    person = models.CharField("person", max_length=128)
    address = models.TextField("address")
    phone = models.TextField("phone")
    fax_no = models.TextField("fax-no", blank=True, null=True)
    email = models.TextField("email")
    rir = models.ForeignKey(RIR, verbose_name="RIR")
    extra = models.TextField("extra", blank=True, null=True)

    def __unicode__(self):
        return u" %s (%s)" % (self.nic_hdl, self.person)

    @property
    def rpsl(self):
        s = []
        s += ["person: %s" % self.person]
        s += ["nic-hdl: %s" % self.nic_hdl]
        s += ["address: %s" % x for x in self.address.split("\n")]
        s += ["phone: %s" % x for x in self.phone.split("\n")]
        if self.fax_no:
            s += ["fax-no: %s" % x for x in self.fax_no.split("\n")]
        s += ["email: %s" % x for x in self.email.split("\n")]
        if self.extra:
            s += [self.extra]
        return rpsl_format("\n".join(s))


class Maintainer(models.Model):
    class Meta:
        verbose_name = "Maintainer"
        verbose_name_plural = "Maintainers"

    maintainer = models.CharField("mntner", max_length=64, unique=True)
    description = models.CharField("description", max_length=64)
    password = models.CharField("Password", max_length=64,
                                null=True, blank=True)
    rir = models.ForeignKey(RIR, verbose_name="RIR")
    admins = models.ManyToManyField(Person, verbose_name="admin-c")
    extra = models.TextField("extra", blank=True, null=True)

    def __unicode__(self):
        return self.maintainer

    @property
    def rpsl(self):
        s = []
        s += ["mntner: %s" % self.maintainer]
        s += ["descr: %s" % self.description]
        if self.password:
            s += ["auth: MD5-PW %s" % md5crypt(self.password)]
        s += ["admins: %s" % x.nic_hdl for x in self.admins.all()]
        s += ["mnt-by: %s" % self.maintainer]
        if self.extra:
            s += [self.extra]
        return rpsl_format("\n".join(s))


class Organisation(models.Model):
    class Meta:
        verbose_name = "Organisation"
        verbose_name_plural = "Organisations"

    # NIC Handle
    organisation = models.CharField("Organisation",
                                    max_length=128, unique=True)
    org_name = models.CharField("Org. Name", max_length=128)  # org-name:
    # org-type
    org_type = models.CharField("Org. Type", max_length=64,
                                choices=[(x, x) for x in
                                    ("IANA", "RIR", "NIR", "LIR", "OTHER")])
    # address: will be prepended automatically for each line
    address = models.TextField("Address")
    mnt_ref = models.ForeignKey(Maintainer, verbose_name="Mnt. Ref")  # mnt-ref

    def __unicode__(self):
        return u" %s (%s)" % (self.organisation, self.org_name)


class AS(models.Model):
    class Meta:
        verbose_name = "AS"
        verbose_name_plural = "ASes"

    asn = models.IntegerField("ASN", unique=True)
    # as-name RPSL Field
    as_name = models.CharField("AS Name", max_length=64, null=True, blank=True)
    # RPSL descr field
    description = models.CharField("Description", max_length=64)
    organisation = models.ForeignKey(Organisation, verbose_name="Organisation")
    administrative_contacts = models.ManyToManyField(Person,
            verbose_name="admin-c", related_name="as_administrative_contacts")
    tech_contacts = models.ManyToManyField(Person, verbose_name="tech-c",
                                           related_name="as_tech_contacts")
    maintainers = models.ManyToManyField(Maintainer, verbose_name="Maintainers",
                                         related_name="as_maintainers")
    routes_maintainers = models.ManyToManyField(Maintainer,
            verbose_name="Routes Maintainers",
            related_name="as_route_maintainers")
    # remarks: will be prepended automatically
    header_remarks = models.TextField("Header Remarks", null=True, blank=True)
     # remarks: will be prepended automatically
    footer_remarks = models.TextField("Footer Remarks", null=True, blank=True)
    rir = models.ForeignKey(RIR, verbose_name="RIR")  # source:
    tags = AutoCompleteTagsField("Tags", null=True, blank=True)

    def __unicode__(self):
        return u"AS%d (%s)" % (self.asn, self.description)

    def get_absolute_url(self):
        return site.reverse("peer:as:change", self.id)

    @classmethod
    def default_as(cls):
        try:
            return AS.objects.get(asn=0)
        except AS.DoesNotExist:
            # Try to create AS0
            rir = RIR.objects.all()[0]
            org = Organisation.objects.all()[0]
            a = AS(asn=0, as_name="Default",
                   description="Default AS, do not delete",
                   rir=rir, organisation=org)
            a.save()
            return a

    @property
    def rpsl(self):
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
        pg = {}  # Peer Group -> AS -> peering_point -> [(import, export, localpref, import_med, export_med, remark)]
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
                if (peer.import_filter == p_import and
                    peer.export_filter == p_export and
                    e_import_med == import_med and
                    e_export_med == export_med):
                    to_skip = True
                    break
            if not to_skip:
                pg[peer.peer_group][peer.remote_asn][peer.peering_point] +=\
                    [(peer.import_filter, peer.export_filter,
                      peer.effective_local_pref, e_import_med, e_export_med,
                      peer.rpsl_remark)]
        # Build RPSL
        inverse_pref = config.getboolean("peer", "rpsl_inverse_pref_style")
        for peer_group in pg:
            s += [sep]
            s += ["remarks: -- %s" % x
                  for x in peer_group.description.split("\n")]
            s += [sep]
            for asn in sorted(pg[peer_group]):
                add_at = len(pg[peer_group][asn]) != 1
                for pp in pg[peer_group][asn]:
                    for R in pg[peer_group][asn][pp]:
                        import_filter, export_filter, localpref, import_med,\
                        export_med, remark = R
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
            s += ["remarks: %s" % x
                  for x in self.footer_remarks.split("\n")]
        return rpsl_format("\n".join(s))

    @property
    def dot(self):
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
        for subgraph, peers in [("uplinks", uplinks.values()),
                                ("peers", peers.values()),
                                ("downlinks", downlinks.values())]:
            s += ["subgraph %s {" % subgraph]
            for p in peers:
                attrs = ["taillabel=\" %s\"" % p.import_filter,
                         "headlabel=\" %s\"" % p.export_filter]
                if p.import_filter == "ANY":
                    attrs += ["arrowtail=open"]
                if p.export_filter == "ANY":
                    attrs += ["arrothead=open"]
                s += ["    %s -- AS%d [%s];" % (asn, p.remote_asn,
                                                ",".join(attrs))]
            s += ["}"]
        s += ["}"]
        return "\n".join(s)

    def update_rir_db(self):
        return self.rir.update_rir_db(self.rpsl, self.maintainers.all()[0])


class CommunityType(models.Model):
    class Meta:
        verbose_name = "Community Type"
        verbose_name_plural = "Community Types"

    name = models.CharField("Description", max_length=32, unique=True)

    def __unicode__(self):
        return self.name


class Community(models.Model):
    class Meta:
        verbose_name = "Community"
        verbose_name_plural = "Communities"

    community = models.CharField("Community", max_length=20, unique=True)
    type = models.ForeignKey(CommunityType, verbose_name="Type")
    description = models.CharField("Description", max_length=64)

    def __unicode__(self):
        return self.community


class ASSet(models.Model):
    class Meta:
        verbose_name = "ASSet"
        verbose_name_plural = "ASSets"

    name = models.CharField("Name", max_length=32, unique=True)
    description = models.CharField("Description", max_length=64)
    members = models.TextField("Members", null=True, blank=True)
    rpsl_header = models.TextField("RPSL Header", null=True, blank=True)
    rpsl_footer = models.TextField("RPSL Footer", null=True, blank=True)
    tags = AutoCompleteTagsField("Tags", null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return site.reverse("peer:asset:change", self.id)

    @property
    def member_list(self):
        if self.members is None:
            return []
        m = sorted(self.members.replace(",", " ")\
                   .replace("\n", " ").replace("\r", " ").upper().split())
        return m

    @property
    def rpsl(self):
        sep = "remark: %s" % ("-" * 72)
        s = []
        if self.rpsl_header:
            s += self.rpsl_header.split("\n")
        s += ["as-set: %s" % self.name]
        for m in self.member_list:
            s += ["members: %s" % m]
        if self.rpsl_footer:
            s += [sep]
            s += self.rpsl_footer.split("\n")
        return rpsl_format("\n".join(s))


class PeeringPoint(models.Model):
    class Meta:
        verbose_name = "Peering Point"
        verbose_name_plural = "Peering Points"

    hostname = models.CharField("FQDN", max_length=64, unique=True)
    location = models.CharField("Location", max_length=64, blank=True, null=True)
    local_as = models.ForeignKey(AS, verbose_name="Local AS")
    router_id = models.IPAddressField("Router-ID", unique=True)
    profile_name = models.CharField("Profile", max_length=128,
                                    choices=profile_registry.choices)
    communities = models.CharField("Import Communities", max_length=128,
                                   blank=True, null=True)
    enable_prefix_list_provisioning = models.BooleanField("Enable Prefix-List Provisioning", default=False)
    prefix_list_notification_group = models.ForeignKey(NotificationGroup,
        verbose_name="Prefix List Notification Group", null=True, blank=True)

    def __unicode__(self):
        if self.location:
            return u" %s (%s)" % (self.hostname, self.location)
        else:
            return self.hostname

    def sync_cm_prefix_list(self):
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


class PeerGroup(models.Model):
    class Meta:
        verbose_name = "Peer Group"
        verbose_name_plural = "Peer Groups"

    name = models.CharField("Name", max_length=32, unique=True)
    description = models.CharField("Description", max_length=64)
    communities = models.CharField("Import Communities", max_length=128,
                                   blank=True, null=True)
    max_prefixes = models.IntegerField("Max. Prefixes", default=100)
    local_pref = models.IntegerField("Local Pref", null=True, blank=True)
    import_med = models.IntegerField("Import MED", blank=True, null=True)
    export_med = models.IntegerField("Export MED", blank=True, null=True)

    def __unicode__(self):
        return unicode(self.name)


class Peer(models.Model):
    """
    BGP Peering session
    """
    class Meta:
        verbose_name = "Peer"
        verbose_name_plural = "Peers"

    peer_group = models.ForeignKey(PeerGroup, verbose_name="Peer Group")
    peering_point = models.ForeignKey(PeeringPoint, verbose_name="Peering Point")
    local_asn = models.ForeignKey(AS, verbose_name="Local AS")
    local_ip = INETField("Local IP")
    local_backup_ip = INETField("Local Backup IP", null=True, blank=True)
    remote_asn = models.IntegerField("Remote AS")
    remote_ip = INETField("Remote IP")
    remote_backup_ip = INETField("Remote Backup IP", null=True, blank=True)
    status = models.CharField("Status", max_length=1, default="A",
                              choices=[("P", "Planned"),
                                       ("A", "Active"),
                                       ("S", "Shutdown")])
    import_filter = models.CharField("Import filter", max_length=64)
    local_pref = models.IntegerField("Local Pref", null=True, blank=True)  # Override PeerGroup.local_pref
    import_med = models.IntegerField("Import MED", blank=True, null=True)  # Override PeerGroup.import_med
    export_med = models.IntegerField("Export MED", blank=True, null=True)  # Override PeerGroup.export_med
    export_filter = models.CharField("Export filter", max_length=64)
    description = models.CharField("Description", max_length=64,
                                   null=True, blank=True)
    rpsl_remark = models.CharField("RPSL Remark", max_length=64,
                                   null=True, blank=True)  # Peer remark to be shown in RPSL
    tt = models.IntegerField("TT", blank=True, null=True)
    communities = models.CharField("Import Communities", max_length=128,
                                   blank=True, null=True)   # In addition to PeerGroup.communities
                                                            # and PeeringPoint.communities
    max_prefixes = models.IntegerField("Max. Prefixes", default=100)
    import_filter_name = models.CharField("Import Filter Name", max_length=64,
                                          blank=True, null=True)
    export_filter_name = models.CharField("Export Filter Name", max_length=64,
                                          blank=True, null=True)
    tags = AutoCompleteTagsField("Tags", null=True, blank=True)

    def __unicode__(self):
        return u" %s (%s@%s)" % (self.remote_asn, self.remote_ip,
                                 self.peering_point.hostname)

    def get_absolute_url(self):
        return site.reverse("peer:peer:change", self.id)

    def save(self):
        if self.import_filter_name is not None and not self.import_filter_name.strip():
            self.import_filter_name = None
        if self.export_filter_name is not None and not self.export_filter_name.strip():
            self.export_filter_name = None
        super(Peer, self).save()
        self.peering_point.sync_cm_prefix_list()

    @property
    def tt_url(self):
        return tt_url(self)

    @property
    def all_communities(self):
        r = {}
        for cl in [self.peering_point.communities, self.peer_group.communities,
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
        " announce %s" % self.export_filter
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
    def get_peer(self, address):
        """
        Get peer by address
        @todo: rewrite with F()

        :param address: Remote address
        :type address: Str
        :returns: Peer instance or None
        """
        cursor = connection.cursor()
        cursor.execute("""SELECT id
                       FROM peer_peer
                       WHERE host(remote_ip) = %s
                            OR host(remote_backup_ip) = %s""",
                            [address, address])
        data = cursor.fetchall()
        if data:
            return Peer.objects.get(id=data[0][0])
        else:
            return None


class WhoisASSetMembers(nosql.Document):
    """
    as-set -> members lookup
    """
    meta = {
        "collection": "noc.whois.asset.members",
        "allow_inheritance": False
    }

    as_set = nosql.StringField(unique=True)
    members = nosql.ListField(nosql.StringField())

    def __unicode__(self):
        return self.as_set

    @classmethod
    def lookup(cls, key):
        v = cls.objects.filter(as_set=key.upper()).first()
        if v is None:
            return []
        else:
            return v.members


class WhoisOriginRoute(nosql.Document):
    """
    origin -> route
    """
    meta = {
        "collection": "noc.whois.origin.route",
        "allow_inheritance": False
    }

    origin = nosql.StringField(unique=True)
    routes = nosql.ListField(nosql.StringField())

    def __unicode__(self):
        return self.as_set

    @classmethod
    def lookup(cls, key):
        v = cls.objects.filter(origin=key.upper()).first()
        if v is None:
            return []
        else:
            return v.routes


class WhoisCache(object):
    """
    Whois cache interface
    """
    @classmethod
    def resolve_as_set(cls, as_set, seen=None, collection=None):
        members = set()
        if seen is None:
            seen = set()
        if collection is None:
            db = nosql.get_db()
            collection = db.noc.whois.asset.members
        for a in as_set.split():
            a = a.upper()
            seen.add(a)
            if is_asn(a[2:]):
                # ASN Given
                members.update([a.upper()])
            else:
                o = collection.find_one({"as_set": a}, fields=["members"])
                if o:
                    for m in [x for x in o["members"] if x not in seen]:
                        members.update(cls.resolve_as_set(m, seen, collection))
        return members

    @classmethod
    def _resolve_as_set_prefixes(cls, as_set):
        db = nosql.get_db()
        collection = db.noc.whois.origin.route
        # Resolve
        prefixes = set()
        for a in cls.resolve_as_set(as_set):
            o = collection.find_one({"origin": a}, fields=["routes"])
            if o:
                prefixes.update(o["routes"])
        return prefixes

    @classmethod
    def resolve_as_set_prefixes(cls, as_set, optimize=None):
        prefixes = cls._resolve_as_set_prefixes(as_set)
        pl_optimize = config.getboolean("peer", "prefix_list_optimization")
        threshold = config.getint("peer", "prefix_list_optimization_threshold")
        if (optimize or
            (optimize is None and pl_optimize and len(prefixes) >= threshold)):
            return set(optimize_prefix_list(prefixes))
        return prefixes

    @classmethod
    def resolve_as_set_prefixes_maxlen(cls, as_set, optimize=None):
        """
        Generate prefixes for as-sets.
        Returns a list of (prefix, min length, max length)
        """
        prefixes = cls._resolve_as_set_prefixes(as_set)
        pl_optimize = config.getboolean("peer", "prefix_list_optimization")
        threshold = config.getint("peer", "prefix_list_optimization_threshold")
        max_len = config.getint("peer", "max_prefix_length")
        if (optimize or
            (optimize is None and pl_optimize and len(prefixes) >= threshold)):
            # Optimization is enabled
            return [(p.prefix, p.mask, m) for p, m
                in optimize_prefix_list_maxlen(prefixes)
                if p.mask <= max_len]
        else:
            # Optimization is disabled
            return [(x.prefix, x.mask, x.mask)
                for x in sorted([IP.prefix(p) for p in prefixes])
                if x.mask <= max_len]

    @classmethod
    def cone_power(cls, as_set, mask):
        """
        Returns amount of prefixes of size _mask_ needed to cover as_set
        """
        n = 0
        for p in cls.resolve_as_set_prefixes(as_set, optimize=True):
            m = int(p.split("/")[1])
            if m <= mask:
                n += long(2 * (mask - m))
        return n


class PrefixListCachePrefix(nosql.EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    
    prefix = nosql.StringField(required=True)
    min = nosql.IntField(required=True)
    max = nosql.IntField(required=True)

    def __unicode__(self):
        return self.prefixes


class PrefixListCache(nosql.Document):
    """
    Prepared prefix-list cache. Can hold IPv4/IPv6 prefixes at same time.
    Prefixes are stored sorted
    """
    meta = {
        "collection": "noc.prefix_list_cache",
        "allow_inheritance": False
    }
    
    peering_point = nosql.ForeignKeyField(PeeringPoint)
    name = nosql.StringField()
    prefixes = nosql.ListField(nosql.EmbeddedDocumentField(PrefixListCachePrefix))
    changed = nosql.DateTimeField()
    pushed = nosql.DateTimeField()

    def __unicode__(self):
        return u" %s/%s" % (self.peering_point.hostname, self.name)

    def cmp_prefixes(self, prefixes):
        """
        Compare cached prefixes with a list of (prefix, min, max)
        """
        return [(c.prefix, c.min, c.max) for c in self.prefixes] == prefixes
