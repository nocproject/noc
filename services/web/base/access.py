# ---------------------------------------------------------------------
# Access control
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
from django.db.models import Q
from noc.aaa.models.permission import Permission as DBPermission


class PermissionDenied(Exception):
    """
    Basic Permission Denied exception
    """


class Permission(object):
    """
    Basic Permission class.
    Each permission must implement ``check`` method
    and optional queryset method
    """

    def __init__(self):
        self.app = None

    def queryset(self, request):
        """
        Get _Q_ object restricting the list of available objects
        """
        return Q()

    def check(self, app, user, obj=None):
        """
        Called to check wrether user has access
        For granular permissions obj=None
        means check user has application access
        """
        raise NotImplementedError()

    def display(self, user):
        """
        Return human-readable representation of permission set
        Applicable only for granular permissions
        """
        return ""

    def __or__(self, r):
        """
        _or_ operator implementation
        """
        return ORPermission(self, r)

    def __and__(self, r):
        """
        _and_ operator implementation
        """
        return ANDPermission(self, r)


class LogicPermision(Permission):
    """
    Boolean logic permission. Used to combine two permissions
    using logic condition
    """

    def __init__(self, left, right):
        super().__init__()
        self.left = left
        self.right = right


class ORPermission(LogicPermision):
    """
    _or_ combination. Permit if either left or right conditions are met
    """

    def check(self, app, user, obj=None):
        return self.left.check(app, user, obj) or self.right.check(app, user, obj)

    def queryset(self, request):
        return self.left.queryset(request) | self.right.queryset(request)


class ANDPermission(LogicPermision):
    """
    _and_ combination. Permit if both left and right conditions are met
    """

    def check(self, app, user, obj=None):
        return self.left.check(app, user, obj) and self.right.check(app, user, obj)

    def queryset(self, request):
        return self.left.queryset(request) & self.right.queryset(request)


class Permit(Permission):
    """
    Always permit
    """

    permit = True

    def check(self, app, user, obj=None):
        return True


class Deny(Permission):
    """
    Always deny
    """

    def check(self, app, user, obj=None):
        return False


class PermitLogged(Permission):
    """
    Permit any authenticated user
    """

    def check(self, app, user, obj=None):
        return user.is_authenticated()


class PermitSuperuser(Permission):
    """
    Permit superusers
    """

    def check(self, app, user, obj=None):
        return user.is_superuser


class HasPerm(Permission):
    """
    Permit if the user has permission _perm_
    """

    def __init__(self, perm):
        super().__init__()
        self.perm = perm

    def __repr__(self):
        if hasattr(self, "perm_id"):
            return "<HasPerm '%s' object at 0x%x>" % (self.perm_id, id(self))
        else:
            return "<HasPerm object at 0x%x>" % id(self)

    def get_permission(self, app):
        if ":" in self.perm:
            return self.perm
        else:
            return "%s:%s:%s" % (app.module, app.app, self.perm)

    def check(self, app, user, obj=None):
        return DBPermission.has_perm(user, self.get_permission(app))
