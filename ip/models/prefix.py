# ---------------------------------------------------------------------
# Prefix model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
import operator
from threading import Lock
from typing import List, Optional, Iterable, Dict, Any

# Third-party modules
from django.db import models, connection
from django.contrib.postgres.fields import ArrayField
from django.db.models.query_utils import Q
from pydantic import RootModel, BaseModel
import cachetools

# NOC modules
from noc.config import config
from noc.core.model.base import NOCModel
from noc.aaa.models.user import User
from noc.project.models.project import Project
from noc.peer.models.asn import AS
from noc.vc.models.vlan import VLAN
from noc.core.model.fields import CIDRField, DocumentReferenceField, CachedForeignKey, PydanticField
from noc.core.validators import check_ipv4_prefix, check_ipv6_prefix, ValidationError
from noc.core.ip import IP, IPv4
from noc.main.models.textindex import full_text_search
from noc.main.models.label import Label
from noc.main.models.remotesystem import RemoteSystem
from noc.inv.models.resourcepool import ResourcePool
from noc.core.translation import ugettext as _
from noc.core.wf.decorator import workflow
from noc.core.model.decorator import on_delete_check
from noc.wf.models.state import State
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from .vrf import VRF
from .afi import AFI_CHOICES
from .prefixprofile import PrefixProfile
from .addressprofile import AddressProfile

id_lock = Lock()


class PoolItem(BaseModel):
    pool: str
    ip_filter: Optional[str] = None


PoolItems = RootModel[List[PoolItem]]


@Label.model
@full_text_search
@workflow
@bi_sync
@change
@on_delete_check(
    ignore=[
        ("ip.PrefixBookmark", "prefix"),
        ("ip.Prefix", "parent"),
        ("ip.Prefix", "ipv6_transition"),
        ("ip.Address", "prefix"),
    ]
)
class Prefix(NOCModel):
    """
    Allocated prefix
    """

    class Meta(object):
        verbose_name = _("Prefix")
        verbose_name_plural = _("Prefixes")
        db_table = "ip_prefix"
        app_label = "ip"
        unique_together = [("vrf", "afi", "prefix")]

    parent = models.ForeignKey(
        "self",
        related_name="children_set",
        verbose_name=_("Parent"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    vrf: "VRF" = CachedForeignKey(
        VRF, verbose_name=_("VRF"), default=VRF.get_global, on_delete=models.CASCADE
    )
    afi: str = models.CharField(_("Address Family"), max_length=1, choices=AFI_CHOICES)
    prefix: str = CIDRField(_("Prefix"))
    name: str = models.CharField(_("Name"), max_length=255, null=True, blank=True)
    profile: "PrefixProfile" = DocumentReferenceField(PrefixProfile, null=False, blank=False)
    asn: "AS" = CachedForeignKey(
        AS,
        verbose_name=_("AS"),
        help_text=_("Autonomous system granted with prefix"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    project: "Project" = CachedForeignKey(
        Project,
        verbose_name="Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prefix_set",
    )
    # VLAN bound to prefix
    vlan: "VLAN" = DocumentReferenceField(VLAN, null=True, blank=True)
    description: str = models.TextField(_("Description"), blank=True, null=True)
    # Pools
    pools: Optional[List[PoolItem]] = PydanticField(
        "Remote System Mapping Items",
        schema=PoolItems,
        blank=True,
        null=True,
        default=list,
    )
    # Labels
    labels = ArrayField(models.CharField(max_length=250), blank=True, null=True, default=list)
    effective_labels = ArrayField(
        models.CharField(max_length=250), blank=True, null=True, default=list
    )
    tt: int = models.IntegerField("TT", blank=True, null=True, help_text=_("Ticket #"))
    state: "State" = DocumentReferenceField(State, null=True, blank=True)
    allocated_till = models.DateField(
        _("Allocated till"),
        null=True,
        blank=True,
        help_text=_("Prefix temporary allocated till the date"),
    )
    ipv6_transition = models.OneToOneField(
        "self",
        related_name="ipv4_transition",
        null=True,
        blank=True,
        limit_choices_to={"afi": "6"},
        on_delete=models.SET_NULL,
    )
    prefix_discovery_policy: str = models.CharField(
        _("Prefix Discovery Policy"),
        max_length=1,
        choices=[("P", "Profile"), ("E", "Enable"), ("D", "Disable")],
        default="P",
        blank=False,
        null=False,
    )
    address_discovery_policy: str = models.CharField(
        _("Address Discovery Policy"),
        max_length=1,
        choices=[("P", "Profile"), ("E", "Enable"), ("D", "Disable")],
        default="P",
        blank=False,
        null=False,
    )
    default_address_profile: Optional["AddressProfile"] = DocumentReferenceField(
        AddressProfile, null=True, blank=True
    )
    source = models.CharField(
        "Source",
        max_length=1,
        choices=[
            ("M", "Manual"),
            ("i", "Interface"),
            ("w", "Whois"),
            ("n", "Neighbor"),
            ("P", "Ping"),
        ],
        null=False,
        blank=False,
        default="M",
    )
    # Last state change
    state_changed = models.DateTimeField("State Changed", null=True, blank=True)
    # Timestamp expired
    expired = models.DateTimeField("Expired", null=True, blank=True)
    # Timestamp of last seen
    last_seen = models.DateTimeField("Last Seen", null=True, blank=True)
    # Timestamp of first discovery
    first_discovered = models.DateTimeField("First Discovered", null=True, blank=True)
    # Reference to remote system object has been imported from
    remote_system = DocumentReferenceField(RemoteSystem, null=True, blank=True)
    # Object id in remote system
    remote_id = models.CharField(max_length=64, null=True, blank=True)
    # Object id in BI
    bi_id = models.BigIntegerField(unique=True)

    csv_ignored_fields = ["parent"]
    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __str__(self):
        return f"{self.vrf.name}({self.afi}): {self.prefix}"

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id: int) -> Optional["Prefix"]:
        return Prefix.objects.filter(id=id).first()

    @classmethod
    def get_by_resource_pool(cls, pool: ResourcePool) -> List["Prefix"]:
        """Getting Prefixes for resource pool"""
        # Include VRF
        q = Q(pools__contains=[{"pool": str(pool.id)}])
        profiles = list(PrefixProfile.objects.filter(pools__pool=pool))
        if profiles:
            q |= Q(profile__in=profiles)
        return list(Prefix.objects.filter(q))

    def iter_pool_settings(self) -> Iterable[PoolItem]:
        """Iterate over pool item"""
        processed = []
        for p in self.pools:
            processed.append(p.pool.id)
            yield p
        for p in self.profile.pools:
            if p.pool.id in processed:
                continue
            yield p

    def get_pool_hints(self, pool) -> Optional[Dict[str, Any]]:
        """Getting pool setting for L2Domain"""
        return {}

    @property
    def has_transition(self) -> bool:
        """
        Check prefix has ipv4/ipv6 transition
        :return:
        """
        if self.is_ipv4:
            return bool(self.ipv6_transition)
        else:
            try:
                # pylint: disable=pointless-statement
                self.ipv4_transition  # noqa
                return True
            except Prefix.DoesNotExist:
                return False

    @classmethod
    def get_parent(cls, vrf, afi, prefix) -> Optional["Prefix"]:
        """
        Get nearest closing prefix
        """
        r = Prefix.objects.filter(vrf=vrf, afi=str(afi)).extra(
            select={"masklen": "masklen(prefix)"},
            where=["prefix >> %s"],
            params=[str(prefix)],
            order_by=["-masklen"],
        )[:1]
        if r:
            return r[0]
        return None

    @property
    def is_ipv4(self) -> bool:
        return self.afi == "4"

    @property
    def is_ipv6(self) -> bool:
        return self.afi == "6"

    @property
    def is_root(self) -> bool:
        """
        Returns true if the prefix is a root of VRF
        """
        return (self.is_ipv4 and self.prefix == "0.0.0.0/0") or (
            self.is_ipv6 and self.prefix == "::/0"
        )

    def clean(self):
        """
        Field validation
        """
        super().clean()
        # Set defaults
        self.afi = "6" if ":" in self.prefix else "4"
        # Check prefix is of AFI type
        if self.is_ipv4:
            check_ipv4_prefix(self.prefix)
        elif self.is_ipv6:
            check_ipv6_prefix(self.prefix)
        # Set defaults, if check self.vrf - raise NotRelatedField
        if not self.vrf_id:
            self.vrf = VRF.get_global()
        if not self.is_root:
            # Set proper parent
            self.parent = Prefix.get_parent(self.vrf, self.afi, self.prefix)
        # Check root prefix have no parent
        if self.is_root and self.parent:
            raise ValidationError("Root prefix cannot have parent")

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_prefix:
            yield "prefix", self.id

    def save(self, *args, **kwargs):
        """
        Save prefix
        """
        self.clean()
        super().save(*args, **kwargs)
        # Rebuild tree if necessary
        # Reconnect children children prefixes
        c = connection.cursor()
        c.execute(
            """
            UPDATE %s
            SET    parent_id=%%s
            WHERE
                    vrf_id=%%s
                AND afi=%%s
                AND prefix << %%s
                AND parent_id=%%s
            """
            % Prefix._meta.db_table,
            [self.id, self.vrf.id, self.afi, self.prefix, self.parent.id if self.parent else None],
        )
        # Reconnect children addresses
        c.execute(
            """
            UPDATE %s
            SET prefix_id=%%s
            WHERE
                    prefix_id=%%s
                AND address << %%s
            """
            % Address._meta.db_table,
            [self.id, self.parent.id if self.parent else None, self.prefix],
        )

    def delete(self, *args, **kwargs):
        """
        Delete prefix
        """
        if self.is_root and not getattr(self, "_disable_delete_protection", False):
            raise ValidationError("Cannot delete root prefix")
        # Reconnect children prefixes
        self.children_set.update(parent=self.parent)
        # Reconnect children addresses
        self.address_set.update(prefix=self.parent)
        # Unlink dual-stack allocations
        # self.clear_transition()
        # Remove bookmarks
        self.prefixbookmark_set.all().delete()
        # Finally delete
        super().delete(*args, **kwargs)

    def delete_recursive(self):
        """
        Delete prefix and all descendancies
        """
        # Unlink dual-stack allocations
        # self.clear_transition()
        # Recursive delete
        # Get nested prefixes
        ids = (
            Prefix.objects.filter(vrf=self.vrf, afi=self.afi)
            .extra(where=["prefix <<= %s"], params=[self.prefix])
            .values_list("id", flat=True)
        )
        #
        # Delete nested addresses
        Address.objects.filter(prefix__in=ids).delete()
        # Delete nested prefixes
        Prefix.objects.filter(id__in=ids).delete()
        # Delete permissions
        PrefixAccess.objects.filter(vrf=self.vrf, afi=self.afi).extra(
            where=["prefix <<= %s"], params=[self.prefix]
        )

    @property
    def maintainers(self):
        """
        List of persons having write access
        @todo: PostgreSQL-independent implementation
        """
        return User.objects.raw(
            """
            SELECT id,username,first_name,last_name
            FROM %s u
            WHERE
                is_active=TRUE
                AND
                    (is_superuser=TRUE
                    OR
                    EXISTS(SELECT id
                           FROM %s a
                           WHERE
                                    user_id=u.id
                                AND vrf_id=%%s
                                AND afi=%%s
                                AND prefix>>=%%s
                                AND can_change=TRUE
                           ))
            ORDER BY username
            """
            % (User._meta.db_table, PrefixAccess._meta.db_table),
            [self.vrf.id, self.afi, self.prefix],
        )

    @property
    def short_description(self) -> str:
        """
        Returns first line of description
        :return:
        """
        if self.description:
            return self.description.split("\n", 1)[0].strip()
        return ""

    @property
    def netmask(self) -> Optional[str]:
        """
        returns Netmask for IPv4
        :return:
        """
        if self.is_ipv4:
            return IPv4(self.prefix).netmask.address
        return None

    @property
    def broadcast(self) -> Optional[str]:
        """
        Returns Broadcast for IPv4
        :return:
        """
        if self.is_ipv4:
            return IPv4(self.prefix).last.address
        return None

    @property
    def wildcard(self) -> Optional[str]:
        """
        Returns Cisco wildcard for IPv4
        :return:
        """
        if self.is_ipv4:
            return IPv4(self.prefix).wildcard.address
        return ""

    @property
    def size(self) -> Optional[int]:
        """
        Returns IPv4 prefix size
        :return:
        """
        if self.is_ipv4:
            return IPv4(self.prefix).size
        return None

    def can_view(self, user) -> bool:
        """
        Returns True if user has view access
        :param user:
        :return:
        """
        return PrefixAccess.user_can_view(user, self.vrf, self.afi, self.prefix)

    def can_change(self, user) -> bool:
        """
        Returns True if user has change access
        :param user:
        :return:
        """
        return PrefixAccess.user_can_change(user, self.vrf, self.afi, self.prefix)

    def has_bookmark(self, user) -> bool:
        """
        Check the user has bookmark on prefix
        :param user:
        :return:
        """
        from .prefixbookmark import PrefixBookmark  # noqa

        return bool(PrefixBookmark.objects.filter(user=user, prefix=self).first())

    def toggle_bookmark(self, user) -> bool:
        """
        Toggle user bookmark. Returns new bookmark state
        :param user:
        :return:
        """
        from .prefixbookmark import PrefixBookmark  # noqa

        b, created = PrefixBookmark.objects.get_or_create(user=user, prefix=self)
        if created:
            return True
        b.delete()
        return False

    def get_index(self):
        """
        Full-text search
        """
        content = [self.prefix]
        card = "Prefix %s" % self.prefix
        if self.description:
            content += [self.description]
            card += " (%s)" % self.description
        r = {
            "id": "ip.prefix:%s" % self.id,
            "title": self.prefix,
            "content": "\n".join(content),
            "card": card,
        }
        if self.labels:
            r["tags"] = self.labels
        return r

    @classmethod
    def get_search_result_url(cls, obj_id) -> str:
        return f"/api/card/view/prefix/{obj_id}/"

    def get_path(self):
        return (
            Prefix.objects.filter(vrf=self.vrf, afi=self.afi)
            .extra(where=["prefix >>= %s"], params=[self.prefix])
            .order_by("prefix")
            .values_list("id", flat=True)
        )

    @property
    def address_ranges(self) -> List["AddressRange"]:
        """
        All prefix-related address ranges
        :return:
        """
        return list(
            AddressRange.objects.raw(
                """
                SELECT *
                FROM ip_addressrange
                WHERE
                        vrf_id=%s
                    AND afi=%s
                    AND is_active=TRUE
                    AND
                        (
                                from_address << %s
                            OR  to_address << %s
                            OR  %s BETWEEN from_address AND to_address
                        )
                ORDER BY from_address, to_address
                """,
                [self.vrf.id, self.afi, self.prefix, self.prefix, self.prefix],
            )
        )

    def rebase(self, vrf, new_prefix) -> Optional["Prefix"]:
        """
        Rebase prefix to a new location
        :param vrf:
        :param new_prefix:
        :return:
        """
        #
        b = IP.prefix(self.prefix)
        nb = IP.prefix(new_prefix)
        # Validation
        if vrf == self.vrf and self.prefix == new_prefix:
            raise ValueError("Cannot rebase to self")
        if b.afi != nb.afi:
            raise ValueError("Cannot change address family during rebase")
        if b.mask < nb.mask:
            raise ValueError("Cannot rebase to prefix of lesser size")
        # Rebase prefix and all nested prefixes
        # Parents are left untouched
        for p in Prefix.objects.filter(vrf=self.vrf, afi=self.afi).extra(
            where=["prefix <<= %s"], params=[self.prefix]
        ):
            np = IP.prefix(p.prefix).rebase(b, nb).prefix
            # Prefix.objects.filter(pk=p.pk).update(prefix=np, vrf=vrf)
            p.prefix = np
            p.vrf = vrf
            p.save()  # Raise events
        # Rebase addresses
        # Parents are left untouched
        for a in Address.objects.filter(vrf=self.vrf, afi=self.afi).extra(
            where=["address <<= %s"], params=[self.prefix]
        ):
            na = IP.prefix(a.address).rebase(b, nb).address
            # Address.objects.filter(pk=a.pk).update(address=na, vrf=vrf)
            a.address = na
            a.vrf = vrf
            a.save()  # Raise events
        # Rebase permissions
        # move all permissions to the nested blocks
        for pa in PrefixAccess.objects.filter(vrf=self.vrf).extra(
            where=["prefix <<= %s"], params=[self.prefix]
        ):
            np = IP.prefix(pa.prefix).rebase(b, nb).prefix
            PrefixAccess.objects.filter(pk=pa.pk).update(prefix=np, vrf=vrf)
        # create permissions for covered blocks
        for pa in PrefixAccess.objects.filter(vrf=self.vrf).extra(
            where=["prefix >> %s"], params=[self.prefix]
        ):
            PrefixAccess(
                user=pa.user,
                vrf=vrf,
                afi=pa.afi,
                prefix=new_prefix,
                can_view=pa.can_view,
                can_change=pa.can_change,
            ).save()
        # @todo: Rebase bookmarks
        # @todo: Update caches
        # Return rebased prefix
        return Prefix.objects.get(pk=self.pk)  # Updated object

    @property
    def nested_prefix_set(self):
        """
        Queryset returning all nested prefixes inside the prefix
        """
        return Prefix.objects.filter(vrf=self.vrf, afi=self.afi).extra(
            where=["prefix <<= %s"], params=[self.prefix]
        )

    @property
    def nested_address_set(self):
        """
        Queryset returning all nested addresses inside the prefix
        """
        return Address.objects.filter(vrf=self.vrf, afi=self.afi).extra(
            where=["address <<= %s"], params=[self.prefix]
        )

    def iter_free(self):
        """
        Generator returning all available free prefixes inside
        :return:
        """
        for fp in IP.prefix(self.prefix).iter_free([p.prefix for p in self.children_set.all()]):
            yield str(fp)

    @property
    def effective_address_discovery(self) -> str:
        if self.address_discovery_policy == "P":
            return self.profile.address_discovery_policy
        return self.address_discovery_policy

    @property
    def effective_prefix_discovery(self) -> str:
        if self.prefix_discovery_policy == "P":
            return self.profile.prefix_discovery_policy
        return self.prefix_discovery_policy

    @property
    def effective_prefix_special_address(self) -> str:
        return self.profile.prefix_special_address_policy

    @property
    def usage(self) -> Optional[float]:
        if self.is_ipv4:
            usage = getattr(self, "_usage_cache", None)
            if usage is not None:
                # Use update_prefixes_usage results
                return usage
            size = IPv4(self.prefix).size
            if not size:
                return 100.0
            n_ips = Address.objects.filter(prefix=self).count()
            if n_ips and size > 2 and self.effective_prefix_special_address == "X":
                # Exclude special addresses
                size -= len(IPv4(self.prefix).special_addresses)
            n_pfx = sum(
                IPv4(p).size
                for p in Prefix.objects.filter(parent=self)
                .only("prefix")
                .values_list("prefix", flat=True)
            )
            return float(n_ips + n_pfx) * 100.0 / float(size)
        return None

    @property
    def usage_percent(self) -> str:
        u = self.usage
        if u is None:
            return ""
        return "%.2f%%" % u

    @staticmethod
    def update_prefixes_usage(prefixes):
        """
        Bulk calculate and update prefixes usages
        :param prefixes: List of Prefix instances
        :return:
        """
        # Filter IPv4 only
        ipv4_prefixes = [p for p in prefixes if p.is_ipv4]
        # Calculate nested prefixes
        usage = defaultdict(int)
        address_usage = defaultdict(int)
        for parent, prefix in Prefix.objects.filter(parent__in=ipv4_prefixes).values_list(
            "parent", "prefix"
        ):
            ln = int(prefix.split("/")[1])
            usage[parent] += 2 ** (32 - ln)
        # Calculate nested addresses
        has_address = set()
        for parent, count in (
            Address.objects.filter(prefix__in=ipv4_prefixes)
            .values("prefix")
            .annotate(count=models.Count("prefix"))
            .values_list("prefix", "count")
        ):
            usage[parent] += count
            has_address.add(parent)
            address_usage[parent] += count
        # Update usage cache
        for p in ipv4_prefixes:
            ln = int(p.prefix.split("/")[1])
            size = 2 ** (32 - ln)
            if p.id in has_address and size > 2:  # Not /31 or /32
                if p.effective_prefix_special_address == "X":
                    size -= 2  # Exclude broadcast and network
            p._address_usage_cache = float(address_usage[p.id]) * 100.0 / float(size)
            p._usage_cache = float(usage[p.id]) * 100.0 / float(size)

    @property
    def address_usage(self) -> Optional[float]:
        if not self.is_ipv4:
            # Fix for ipv6
            return None
        usage = getattr(self, "_address_usage_cache", None)
        if usage is not None:
            # Use update_prefixes_usage results
            return usage
        size = IPv4(self.prefix).size
        if not size:
            return 100.0
        n_ips = (
            Address.objects.filter(vrf=self.vrf, afi=self.afi)
            .extra(where=["address <<= %s"], params=[str(self.prefix)])
            .count()
        )
        if not n_ips:
            return 0.0
        if self.effective_prefix_special_address == "X":
            n_pfx = (
                Prefix.objects.filter(vrf=self.vrf, afi=self.afi)
                .extra(where=["prefix <<= %s"], params=[str(self.prefix)])
                .count()
            )
            size -= len(IPv4(self.prefix).special_addresses) * n_pfx
        return float(n_ips) * 100.0 / float(size) if size else 100.0

    @property
    def address_usage_percent(self) -> str:
        u = self.address_usage
        if u is None:
            return ""
        return "%.2f%%" % u

    def is_empty(self) -> bool:
        """
        Check prefix is empty and does not contain nested prefixes
        and addresses
        :return:
        """
        if Prefix.objects.filter(parent=self).count() > 0:
            return False
        if Address.objects.filter(prefix=self).count() > 0:
            return False
        return True

    def disable_delete_protection(self):
        """
        Disable root delete protection
        :return:
        """
        self._disable_delete_protection = True

    def get_effective_as(self) -> Optional["AS"]:
        """
        Return effective AS (first found upwards)
        :return: AS instance or None
        """
        if self.asn:
            return self.asn
        if not self.parent:
            return None
        return self.parent.get_effective_as()

    def get_effective_address_profile(self) -> Optional["AddressProfile"]:
        """Return effective Address Profile (first found upwards)"""
        if self.default_address_profile:
            return self.default_address_profile
        elif self.profile.default_address_profile:
            return self.profile.default_address_profile
        if not self.parent:
            return None
        return self.parent.get_effective_address_profile()

    def get_default_address_profile(self) -> AddressProfile:
        p = self.get_effective_address_profile()
        if p:
            return p
        return AddressProfile.get_default_profile()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_ipprefix")


# Avoid circular references
from .address import Address
from .prefixaccess import PrefixAccess
from .addressrange import AddressRange
