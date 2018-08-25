# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# LDAP Authentication backend
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
import ldap3
# NOC modules
from noc.main.models.authldapdomain import AuthLDAPDomain
from .base import BaseAuthBackend


class LdapBackend(BaseAuthBackend):
    def authenticate(self, user=None, password=None, **kwargs):
        # Get domain
        domain, user = self.split_user_domain(user)
        if domain:
            ldap_domain = AuthLDAPDomain.get_by_name(domain)
            if not ldap_domain:
                self.logger.error(
                    "LDAP Auth domain '%s' is not configured",
                    domain
                )
                raise self.LoginError(
                    "Invalid LDAP domain '%s'" % domain
                )
        else:
            ldap_domain = AuthLDAPDomain.get_default_domain()
            if not ldap_domain:
                self.logger.error(
                    "Default LDAP Auth domain is not configured"
                )
                raise self.LoginError("Default LDAP domain is not configured")
        if not ldap_domain.is_active:
            self.logger.error(
                "LDAP Auth domain '%s' is disabled",
                domain
            )
            raise self.LoginError(
                "LDAP Auth domain '%s' is disabled" % domain
            )
        # Get servers
        server_pool = self.get_server_pool(ldap_domain)
        if not server_pool:
            self.logger.error(
                "No active servers configured for domain '%s'", domain
            )
            raise self.LoginError(
                "No active servers configured for domain '%s'" % domain
            )
        # Connect and bind
        connect_kwargs = self.get_connection_kwargs(ldap_domain, user, password)
        dkw = connect_kwargs.copy()
        if "password" in dkw:
            dkw["password"] = "******"
        self.logger.debug("Connect to ldap: %s", ", ".join(
            "%s='%s'" % (kk, dkw[kk]) for kk in dkw)
        )
        connect = ldap3.Connection(server_pool, **connect_kwargs)
        if not connect.bind():
            raise self.LoginError(
                "Failed to bind to LDAP: %s" % connect.result
            )
        # Rebind as privileged user
        if ldap_domain.bind_user:
            # Rebind as privileged user
            connect = ldap3.Connection(
                server_pool,
                **self.get_connection_kwargs(
                    ldap_domain,
                    ldap_domain.bind_user, ldap_domain.bind_password
                )
            )
            if not connect.bind():
                self.logger.error(
                    "Cannot bind as %s to search groups",
                    ldap_domain.bind_user
                )
                connect = None
        # Get user information
        user_info = self.get_user_info(connect, ldap_domain, user)
        user_info["user"] = user
        user_info["domain"] = domain
        user_info["is_active"] = True
        # Get user groups
        user_groups = set(g.lower() for g in self.get_user_groups(connect, ldap_domain, user_info))
        if ldap_domain.require_any_group and not user_groups:
            self.logger.error(
                "User %s in not a member of any mapped groups. Deny access",
                user
            )
            raise self.LoginError("No groups")
        if ldap_domain.require_group and ldap_domain.require_group.lower() not in user_groups:
            self.logger.error(
                "User %s is not a member of required group %s but member of %s",
                user, ldap_domain.require_group, user_groups
            )
            raise self.LoginError("Login is not permitted")
        if ldap_domain.deny_group and ldap_domain.deny_group.lower() in user_groups:
            self.logger.error(
                "User %s is a member of deny group %s",
                user, ldap_domain.deny_group
            )
            user_info["is_active"] = False
        # Synchronize user
        user = ldap_domain.clean_username(user)
        u = self.ensure_user(user, **user_info)
        # Get group mappings
        group_mappings = ldap_domain.get_group_mappings()
        # Apply groups
        ug = []
        for group in group_mappings:
            if group_mappings[group] & user_groups:
                self.logger.debug(
                    "%s: Ensure group %s",
                    u.username, group.name
                )
                self.ensure_group(u, group)
                ug += [group.name]
            else:
                self.logger.debug(
                    "%s: Deny group %s",
                    u.username, group.name
                )
                self.deny_group(u, group)
        # Final check
        if not user_info["is_active"]:
            raise self.LoginError("Access denied")
        self.logger.info(
            "Authenticated as %s. Groups: %s",
            u.username, ", ".join(ug)
        )
        return u.username

    @classmethod
    def split_user_domain(cls, user):
        """
        Split domain from user name.
        Acceptable forms are
        DOMAIN\User
        User@DOMAIN
        :param username: Username
        :return: (domain, user)
        """
        if "\\" in user:
            return user.split("\\", 1)
        if "@" in user:
            u, d = user.rsplit("@", 1)
            return d, u
        return None, user

    def get_server_pool(self, ldap_domain):
        servers = []
        for s in ldap_domain.servers:
            if not s.is_active:
                continue
            kwargs = {
                "host": s.address
            }
            if s.port:
                kwargs["port"] = s.port
            if s.use_tls:
                kwargs["use_ssl"] = True
            servers += [ldap3.Server(**kwargs)]
        if not servers:
            self.logger.error(
                "No active servers configured for domain '%s'",
                ldap_domain.name
            )
            return None
        pool = ldap3.ServerPool(
            servers,
            ldap3.POOLING_STRATEGY_ROUND_ROBIN
        )
        return pool

    def get_connection_kwargs(self, ldap_domain, user, password):
        """
        Return LDAP connection instance
        :param ldap_domain:
        :param user:
        :param password:
        :return:
        """
        if ldap_domain.type == "ad":
            if "\\" not in user and "@" not in user:
                user = "%s\%s" % (ldap_domain.name, user)
            kwargs = {
                "user": user,
                "authentication": ldap3.NTLM
            }
        else:
            kwargs = {
                "user": "uid=%s,%s" % (user, ldap_domain.get_user_search_dn())
            }
        kwargs["password"] = password
        return kwargs

    def get_user_info(self, connection, ldap_domain, user):
        user_info = {
            "user_dn": user
        }
        if not connection:
            return user_info
        usf = ldap_domain.get_user_search_filter() % {"user": user}
        user_search_dn = ldap_domain.get_user_search_dn()
        self.logger.debug("User search from %s: %s",
                          user_search_dn, usf)
        connection.search(
            user_search_dn,
            ldap_domain.get_user_search_filter() % {"user": user},
            ldap3.SUBTREE,
            attributes=ldap_domain.get_user_search_attributes()
        )
        if not connection.entries:
            self.logger.info("Cannot find user %s", user)
            return user_info
        entry = connection.entries[0]
        attrs = entry.entry_get_attributes_dict()
        self.logger.debug("User attributes: %s", attrs if attrs else "No attributes response")
        user_info["user_dn"] = entry.entry_get_dn()
        for k, v in ldap_domain.get_attr_mappings().items():
            if k in attrs:
                value = attrs[k]
                if isinstance(value, (list, tuple)):
                    value = " ".join(value)
                user_info[v] = value
        if "mail" in user_info and not ldap_domain.sync_mail:
            del user_info["mail"]
        if "first_name" in user_info and not ldap_domain.sync_name:
            del user_info["first_name"]
        if "last_name" in user_info and not ldap_domain.sync_name:
            del user_info["last_name"]
        return user_info

    def get_user_groups(self, connection, ldap_domain, user_info):
        if not connection:
            self.logger.debug("No active connection")
            return []
        group_search_dn = ldap_domain.get_group_search_dn()
        gsf = ldap_domain.get_group_search_filter() % user_info
        self.logger.debug("Group search from %s: %s",
                          group_search_dn, gsf)
        connection.search(
            group_search_dn,
            gsf,
            ldap3.SUBTREE,
            attributes=["cn"]
        )
        self.logger.debug("Groups found: %s",
                          [e.entry_get_dn() for e in connection.entries])
        return [e.entry_get_dn() for e in connection.entries]
