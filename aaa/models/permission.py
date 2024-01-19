# ---------------------------------------------------------------------
# Permission database model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional
import operator

# Third-party modules
from django.db.models import CharField, ManyToManyField
import cachetools

# NOC modules
from noc.core.model.base import NOCModel
from noc.aaa.models.user import User
from noc.aaa.models.group import Group

perm_lock = Lock()
id_lock = Lock()


class Permission(NOCModel):
    """
    Permissions.

    Populated by manage.py sync-perm
    @todo: Check name format
    """

    class Meta(object):
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        db_table = "main_permission"
        app_label = "aaa"

    # module:app:permission
    name = CharField("Name", max_length=128, unique=True)
    # comma-separated list of permissions
    implied = CharField("Implied", max_length=256, null=True, blank=True)
    users = ManyToManyField(User, related_name="permissions")
    groups = ManyToManyField(Group, related_name="permissions")

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _effective_perm_cache = cachetools.TTLCache(maxsize=100, ttl=3)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id: int) -> Optional["Permission"]:
        p = Permission.objects.filter(id=id)[:1]
        if p:
            return p[0]
        return None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        p = Permission.objects.filter(name=name)[:1]
        if p:
            return p[0]
        return None

    def get_implied_permissions(self):
        if not self.implied:
            return []
        return [Permission.objects.get(name=p.strip()) for p in self.implied.split(",")]

    @classmethod
    def has_perm(cls, user, perm):
        """
        Check user has permission either directly either via groups
        """
        if not user.is_active:
            return False
        if user.is_superuser:
            return True
        return perm in cls.get_effective_permissions(user)

    @classmethod
    def get_user_permissions(cls, user):
        """
        Return a set of user permissions
        """
        return set(user.permissions.values_list("name", flat=True))

    @classmethod
    def set_user_permissions(cls, user, perms):
        """
        Set user permissions

        :param user: User
        :type user: User
        :param perms: Set of new permissions
        :type perms: Set
        """
        # Add implied permissions
        perms = set(perms)  # Copy
        for p in cls.objects.filter(name__in=list(perms), implied__isnull=False):
            perms.update([x.strip() for x in p.implied.split(",")])
        #
        current = cls.get_user_permissions(user)
        # Add new permissions
        for p in perms - current:
            try:
                Permission.objects.get(name=p).users.add(user)
            except Permission.DoesNotExist:
                raise Permission.DoesNotExist("Permission '%s' does not exist" % p)
        # Revoke permission
        for p in current - perms:
            Permission.objects.get(name=p).users.remove(user)

    @classmethod
    def get_group_permissions(cls, group):
        """
        Get set of group permissions
        """
        return set(group.permissions.values_list("name", flat=True))

    @classmethod
    def set_group_permissions(cls, group, perms):
        """
        Set group permissions

        :param group: Group
        :type group: Group
        :param perms: Set of permissions
        :type perms: Set
        """
        # Add implied permissions
        perms = set(perms)  # Copy
        for p in cls.objects.filter(name__in=list(perms), implied__isnull=False):
            perms.update([x.strip() for x in p.implied.split(",")])
        #
        current = cls.get_group_permissions(group)
        # Add new permissions
        for p in perms - current:
            Permission.objects.get(name=p).groups.add(group)
        # Revoke permissions
        for p in current - perms:
            Permission.objects.get(name=p).groups.remove(group)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_effective_perm_cache"), lock=lambda _: perm_lock)
    def get_effective_permissions(cls, user):
        """
        Returns a set of effective user permissions,
        counting group and implied ones
        """
        if user.is_superuser:
            return set(Permission.objects.values_list("name", flat=True))
        perms = set()
        # User permissions
        for p in user.permissions.all():
            perms.add(p.name)
            if p.implied:
                perms.update(p.implied.split(","))
        # Group permissions
        for g in user.groups.all():
            for p in g.permissions.all():
                perms.add(p.name)
                if p.implied:
                    perms.update(p.implied.split(","))
        return perms

    @classmethod
    def sync(cls):
        from noc.services.web.base.site import site

        def normalize(app, perm):
            if ":" in perm:
                return perm
            return "%s:%s" % (app.get_app_id().replace(".", ":"), perm)

        def get_implied(name):
            try:
                return ",".join(implied_permissions[name])
            except KeyError:
                return None

        if not site.apps:
            # Initialize applications to get permissions
            site.autodiscover()
        new_perms = set()
        implied_permissions = {}
        diverged_permissions = {}  # new -> old
        for app in site.apps.values():
            new_perms = new_perms.union(app.get_permissions())
            for p in app.implied_permissions:
                ips = sorted([normalize(app, pp) for pp in app.implied_permissions[p]])
                implied_permissions[normalize(app, p)] = ips
            for p in app.diverged_permissions:
                diverged_permissions[normalize(app, p)] = normalize(
                    app, app.diverged_permissions[p]
                )
        # Check all implied permissions are present
        for p in implied_permissions:
            if p not in new_perms:
                raise ValueError("Implied permission '%s' is not found" % p)
            nf = [pp for pp in implied_permissions[p] if pp not in new_perms]
            if nf:
                raise ValueError("Invalid implied permissions: %s" % nf)
        #
        old_perms = set(Permission.objects.values_list("name", flat=True))
        # New permissions
        created_perms = {}  # name -> permission
        for name in new_perms - old_perms:
            # @todo: add implied permissions
            p = Permission(name=name, implied=get_implied(name))
            p.save()
            print("+ %s" % name)
            created_perms[name] = p
        # Check implied permissions match
        for name in old_perms.intersection(new_perms):
            implied = get_implied(name)
            p = Permission.objects.get(name=name)
            if p.implied != implied:
                print("~ %s" % name)
                p.implied = implied
                p.save()
        # Deleted permissions
        for name in old_perms - new_perms:
            print("- %s" % name)
            Permission.objects.get(name=name).delete()
        # Diverge created permissions
        for name in created_perms:
            op_name = diverged_permissions.get(name)
            if not op_name:
                continue
            # Ger original permission
            op = Permission.get_by_name(op_name)
            if not op:
                continue
            print(": %s -> (%s, %s)" % (op_name, op_name, name))
            # Migrate users
            dp = created_perms[name]
            for u in op.users.all():
                dp.users.add(u)
            # Migrate groups
            for g in op.groups.all():
                dp.groups.add(g)
