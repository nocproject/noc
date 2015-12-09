# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Premission database model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
from django.contrib.auth.models import User, Group
## NOC modules
from noc.lib.middleware import get_request


class Permission(models.Model):
    """
    Permissions.

    Populated by manage.py sync-perm
    @todo: Check name format
    """
    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        db_table = "main_permission"
        app_label = "main"

    # module:app:permission
    name = models.CharField("Name", max_length=128, unique=True)
    # comma-separated list of permissions
    implied = models.CharField(
        "Implied", max_length=256, null=True, blank=True)
    users = models.ManyToManyField(
        User, related_name="noc_user_permissions")
    groups = models.ManyToManyField(
        Group, related_name="noc_group_permissions")

    def __unicode__(self):
        return self.name

    def get_implied_permissions(self):
        if not self.implied:
            return []
        return [Permission.objects.get(name=p.strip())
                for p in self.implied.split(",")]

    @classmethod
    def has_perm(cls, user, perm):
        """
        Check user has permission either directly either via groups
        """
        if not user.is_active:
            return False
        if user.is_superuser:
            return True
        request = get_request()
        if request and "PERMISSIONS" in request.session:
            return perm in request.session["PERMISSIONS"]
        else:
            return perm in cls.get_effective_permissions(user)

    @classmethod
    def get_user_permissions(cls, user):
        """
        Return a set of user permissions
        """
        return set(user.noc_user_permissions.values_list("name",
                                                         flat=True))

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
        for p in cls.objects.filter(
                name__in=list(perms), implied__isnull=False):
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
        return set(group.noc_group_permissions.values_list("name",
                                                           flat=True))

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
        for p in cls.objects.filter(
                name__in=list(perms), implied__isnull=False):
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
    def get_effective_permissions(cls, user):
        """
        Returns a set of effective user permissions,
        counting group and implied ones
        """
        if user.is_superuser:
            return set(Permission.objects.values_list(
                "name", flat=True))
        perms = set()
        # User permissions
        for p in user.noc_user_permissions.all():
            perms.add(p.name)
            if p.implied:
                perms.update(p.implied.split(","))
        # Group permissions
        for g in user.groups.all():
            for p in g.noc_group_permissions.all():
                perms.add(p.name)
                if p.implied:
                    perms.update(p.implied.split(","))
        return perms

    @classmethod
    def sync(cls):
        from noc.lib.app import site

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
        for app in site.apps.values():
            new_perms = new_perms.union(app.get_permissions())
            for p in app.implied_permissions:
                ips = sorted([normalize(app, pp)
                              for pp in app.implied_permissions[p]])
                implied_permissions[normalize(app, p)] = ips
        # Check all implied permissions are present
        for p in implied_permissions:
            if p not in new_perms:
                raise ValueError("Implied permission '%s' is not found" % p)
            nf = [pp for pp in implied_permissions[p] if pp not in new_perms]
            if nf:
                raise ValueError("Invalid implied permissions: %s" % pp)
        #
        old_perms = set(Permission.objects.values_list("name", flat=True))
        # New permissions
        for name in new_perms - old_perms:
            # @todo: add implied permissions
            Permission(name=name, implied=get_implied(name)).save()
            print "+ %s" % name
        # Check impiled permissions match
        for name in old_perms.intersection(new_perms):
            implied = get_implied(name)
            p = Permission.objects.get(name=name)
            if p.implied != implied:
                print "~ %s" % name
                p.implied = implied
                p.save()
        # Deleted permissions
        for name in old_perms - new_perms:
            print "- %s" % name
            Permission.objects.get(name=name).delete()

    @classmethod
    def schedule_sync(cls):
        from noc.lib.scheduler.utils import sliding_job
        sliding_job("main.jobs", "main.sync_permissions")
