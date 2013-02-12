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
