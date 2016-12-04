# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## LDAP Authentication backend
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import ldap3
## NOC modules
from base import BaseAuthBackend
from noc.main.models.authldapdomain import AuthLDAPDomain


class LdapBackend(BaseAuthBackend):
    def authenticate(self, user=None, password=None, **kwargs):
        # Get domain
        domain, user = self.split_user_domain(user)
        ldap_domain = AuthLDAPDomain.get_by_name(domain)
        if not ldap_domain:
            self.logger.error(
                "LDAP Auth domain '%s' is not configured",
                domain
            )
            raise self.LoginError(
                "Invalid LDAP domain '%s'" % domain
            )
        # Get servers
        server_pool = self.get_server_pool(ldap_domain)
        if not server_pool:
            raise self.LoginError(
                "No active servers configured for domain '%s'" % domain
            )
        # Connect and bind
        connect = ldap3.Connection(
            server_pool,
            **self.get_connection_kwargs(ldap_domain, user, password)
        )
        if not connect.bind():
            raise self.LoginError(
                "Failed to bind to LDAP: %s",
                connect.result
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
        user_groups = set(self.get_user_groups(connect, ldap_domain, user_info))
        if ldap_domain.require_group and ldap_domain.require_group not in user_groups:
            self.logger.error(
                "User %s is not a member of required group %s",
                user, ldap_domain.require_group
            )
            raise self.LoginError("Login is not permitted")
        if ldap_domain.deny_group:
            self.logger.error(
                "User %s is a member of deny group %s",
                user, ldap_domain.deny_group
            )
            user_info["is_active"] = False
        u = self.ensure_user(user, **user_info)
        # Apply groups
        for g in ldap_domain.groups:
            if not g.is_active:
                continue
            if g.group_dn in user_groups:
                self.ensure_group(u, g.group)
            else:
                self.deny_group(u, g.group)
        # Final check
        if not user_info["is_active"]:
            raise self.LoginError("Access denied")

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
        return AuthLDAPDomain.DEFAULT_DOMAIN, user

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
                "user": user
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
        self.logger.debug("User search from %s: %s",
                          ldap_domain.root, usf)
        connection.search(
            ldap_domain.root,
            ldap_domain.get_user_search_filter() % {"user": user},
            ldap3.SUBTREE
        )
        if not connection.entries:
            self.logger.info("Cannot find user %s", user)
            return user_info
        user_info["user_dn"] = connection.entries[0].entry_dn
        # @todo: Map additional attributes
        return user_info

    def get_user_groups(self, connection, ldap_domain, user_info):
        if not connection:
            return []
        gsf = ldap_domain.get_group_search_filter() % user_info
        self.logger.debug("Group search from %s: %s",
                          ldap_domain.root, gsf)
        connection.search(
            ldap_domain.root,
            gsf,
            ldap3.SUBTREE,
            attributes=["cn"]
        )
        return [e.entry_dn for e in connection.entries]
