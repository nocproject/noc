# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC Authentication backend base class
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## Django modules
from django.contrib.auth.models import User as DjangoUser
## NOC modules
from noc.settings import config


class NOCAuthBackend(object):
    """

    """
    User = DjangoUser
    
    can_change_credentials = False
    supports_object_permissions = False
    supports_anonymous_user = False

    def get_user(self, user_id):
        """
        Get User instance by id or None if user is not found
        """
        try:
            return self.User.objects.get(pk=user_id)
        except self.User.DoesNotExist:
            return None

    def authenticate(self, **kwargs):
        raise NotImplementedError

    def change_credentials(self, user, **kwargs):
        raise NotImplementedError

    def get_or_create_db_user(self, username, is_active=None, is_superuser=None,
                              first_name=None, last_name=None, email=None):
        def maybe_update(instance, attr, value):
            """
            Update instance attr with value, if value is not None.
            Returns True if instance has been updated
            """
            if value is not None and getattr(instance, attr) != value:
                setattr(instance, attr, value)
                return True
            return False

        changed = False
        try:
            user = self.User.objects.get(username=username)
        except self.User.DoesNotExist:
            user = self.User(username=username)
            changed = True
        changed |= maybe_update(user, "is_staff", True)
        changed |= maybe_update(user, "is_active", is_active)
        changed |= maybe_update(user, "is_superuser", is_superuser)
        changed |= maybe_update(user, "first_name", first_name)
        changed |= maybe_update(user, "last_name", last_name)
        changed |= maybe_update(user, "email", email)
        if changed:
            logging.info("Updating user '%s'" % username)
            user.save()
        return user

    def get_login_fields(self):
        return [
            {
                "xtype": "textfield",
                "name": "username",
                "fieldLabel": "Name",
                "allowBlank": False,
                "emptyText": "Enter username"
            },
    
            {
                "xtype": "textfield",
                "name": "password",
                "fieldLabel": "Password",
                "allowBlank": False,
                "inputType": "password"
            }
        ]

    def get_change_credentials_fields(self):
        return [
            {
                "xtype": "textfield",
                "name": "old_password",
                "fieldLabel": "Old Password",
                "allowBlank": False,
                "inputType": "password"
            },

            {
                "xtype": "textfield",
                "name": "new_password",
                "fieldLabel": "New Password",
                "allowBlank": False,
                "inputType": "password"
            },

            {
                "xtype": "textfield",
                "name": "retype_password",
                "fieldLabel": "Retype New Password",
                "allowBlank": False,
                "inputType": "password"
            }
        ]


def get_backend():
    """
    Get current authentication backend's instance
    """
    method = config.get("authentication", "method")
    if method == "local":
        import localbackend
        return localbackend.NOCLocalBackend()
    elif method == "http":
        import httpbackend
        return httpbackend.NOCHTTPBackend()
    elif method == "ldap":
        import ldapbackend
        return ldapbackend.NOCLDAPBackend()
    elif method == "ad":
        import adbackend
        return adbackend.NOCADBackend()
    elif method == "pyrule":
        import pyrulebackend
        return pyrulebackend.NOCPyRuleBackend()
    else:
        raise ValueError("Invalid authentication method '%s'" % method)
