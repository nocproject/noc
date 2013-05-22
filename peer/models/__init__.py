# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Peer module models
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models, connection
## NOC modules
from noc.settings import config
from noc.lib.validators import is_asn
from noc.lib.tt import tt_url
from noc.lib.rpsl import rpsl_format
from noc.lib.fields import INETField, TagsField
from noc.sa.profiles import profile_registry
from noc.main.models import NotificationGroup
from noc.lib.app.site import site
from noc.peer.tree import optimize_prefix_list, optimize_prefix_list_maxlen
from noc.lib import nosql



from rir import RIR
from person import Person
from maintainer import Maintainer
from organisation import Organisation
from asn import AS


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

from asset import ASSet


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
    tags = TagsField("Tags", null=True, blank=True)

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
