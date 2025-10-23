# ---------------------------------------------------------------------
# LDAP Authentication backend
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
import ldap3
from ldap3.utils.conv import escape_filter_chars
from ldap3.core.exceptions import LDAPCommunicationError, LDAPServerPoolExhaustedError

# NOC modules
from noc.main.models.authldapdomain import AuthLDAPDomain
from .base import BaseAuthBackend


class LdapBackend(BaseAuthBackend):
    POOLING_STRATEGIES = {
        "f": ldap3.FIRST,
        "rr": ldap3.ROUND_ROBIN,
        "r": ldap3.RANDOM,
    }

    def authenticate(self, user: str = None, password: str = None, **kwargs) -> str:
        # Validate username
        if not self.check_user(user):
            self.logger.error("Invalid username: %s", user)
            raise self.LoginError("Invalid username")
        # Get domain
        domain, user = self.split_user_domain(user)
        if domain:
            ldap_domain = AuthLDAPDomain.get_by_name(domain)
            if not ldap_domain:
                self.logger.error("LDAP Auth domain '%s' is not configured", domain)
                raise self.LoginError(f"Invalid LDAP domain '{domain}'")
        else:
            ldap_domain = AuthLDAPDomain.get_default_domain()
            if not ldap_domain:
                self.logger.error("Default LDAP Auth domain is not configured")
                raise self.LoginError("Default LDAP domain is not configured")
        if not ldap_domain.is_active:
            self.logger.error("LDAP Auth domain '%s' is disabled", domain)
            raise self.LoginError(f"LDAP Auth domain '{domain}' is disabled")
        # Get servers
        server_pool = self.get_server_pool(ldap_domain)
        if not server_pool:
            self.logger.error("No active servers configured for domain '%s'", domain)
            raise self.LoginError(f"No active servers configured for domain '{domain}'")
        # Get user information
        if ldap_domain.type == "ad":
            # Auth and get user_info
            connect = self.get_server_connection(ldap_domain, server_pool, user, password)
            user_info = self.get_user_info(connect, ldap_domain, user)
        else:
            # Get User Info and Check Auth
            connect = self.get_server_connection(ldap_domain, server_pool)
            user_info = self.get_user_info(connect, ldap_domain, user)
            # Check user Auth
            connect = self.get_server_connection(
                ldap_domain, server_pool, user_info["user_dn"], password
            )
        user_info["user"] = user
        user_info["domain"] = domain
        user_info["is_active"] = True
        # Default ldap3 convert user_dn:
        user_info["user_dn"] = escape_filter_chars(user_info.get("user_dn"))
        # Get user groups
        user_groups = {g.lower() for g in self.get_user_groups(connect, ldap_domain, user_info)}
        if ldap_domain.require_any_group and not user_groups:
            self.logger.error("User %s in not a member of any mapped groups. Deny access", user)
            raise self.LoginError("No groups")
        if ldap_domain.require_group and ldap_domain.require_group.lower() not in user_groups:
            self.logger.error(
                "User %s is not a member of required group %s but member of %s",
                user,
                ldap_domain.require_group,
                user_groups,
            )
            raise self.LoginError("Login is not permitted")
        if ldap_domain.deny_group and ldap_domain.deny_group.lower() in user_groups:
            self.logger.error("User %s is a member of deny group %s", user, ldap_domain.deny_group)
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
                self.logger.debug("%s: Ensure group %s", u.username, group.name)
                self.ensure_group(u, group)
                ug += [group.name]
            else:
                self.logger.debug("%s: Deny group %s", u.username, group.name)
                self.deny_group(u, group)
        # Final check
        if not user_info["is_active"]:
            raise self.LoginError("Access denied")
        self.logger.info("Authenticated as %s. Groups: %s", u.username, ", ".join(ug))
        return u.username

    @classmethod
    def check_user(cls, user):
        """
        Check user has appropriate format
        """
        return user.count("\\") + user.count("@") <= 1

    @classmethod
    def split_user_domain(cls, user):
        r"""
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
            kwargs = {"host": s.address, "connect_timeout": s.connect_timeout}
            if s.port:
                kwargs["port"] = s.port
            if s.use_tls:
                kwargs["use_ssl"] = True
            servers += [ldap3.Server(**kwargs)]
        ldap3.set_config_parameter("POOLING_LOOP_TIMEOUT", 3)
        self.logger.debug(
            "Connect to Servers: %s, %s",
            servers,
            ldap3.get_config_parameter("POOLING_LOOP_TIMEOUT"),
        )
        if not servers:
            self.logger.error("No active servers configured for domain '%s'", ldap_domain.name)
            return None
        return ldap3.ServerPool(
            servers,
            self.POOLING_STRATEGIES.get(ldap_domain.ha_policy),
            active=ldap_domain.get_pool_active(),
            exhaust=ldap_domain.get_pool_exhaust(),
        )

    def get_server_connection(
        self,
        ldap_domain: "AuthLDAPDomain",
        server_pool: "ldap3.ServerPool",
        user: Optional[str] = None,
        password: Optional[str] = None,
    ) -> "ldap3.Connection":
        # Connect and bind
        if not user and not ldap_domain.bind_user:
            raise self.LoginError("Failed to bind to LDAP: Bind User is not set")
        if not user:
            self.logger.debug("Use Bind User credential for connect")
            connect_kwargs = {"user": ldap_domain.bind_user, "password": ldap_domain.bind_password}
        else:
            connect_kwargs = self.get_connection_kwargs(ldap_domain, user, password)
            dkw = connect_kwargs.copy()
            if "password" in dkw:
                dkw["password"] = "******"
            self.logger.debug("Connect to ldap: %s", ", ".join(f"{kk}='{dkw[kk]}'" for kk in dkw))
        connect = ldap3.Connection(server_pool, **connect_kwargs)
        try:
            self.logger.debug("Bind to ldap")
            if not connect.bind():
                raise self.LoginError(f"Failed to bind to LDAP: {connect.result}")
        except (LDAPCommunicationError, LDAPServerPoolExhaustedError) as e:
            self.logger.error("Failed to bind to LDAP: connect failed by %s" % e)
            raise self.LoginError(f"Failed to bind to LDAP: connect failed by {e}")
        return connect

    def get_connection_kwargs(self, ldap_domain: "AuthLDAPDomain", user: str, password: str):
        """
        Return LDAP connection instance
        :param ldap_domain:
        :param user:
        :param password:
        :return:
        """
        if ldap_domain.type == "ad":
            if "\\" not in user and "@" not in user:
                user = r"%s\%s" % (ldap_domain.name, user)
            kwargs = {"user": user, "authentication": ldap3.NTLM}
        else:
            # For Open LDAP userDN getting used bind_user, because it used for bind operation
            # otherwise use _user_search_dn for user OU
            # kwargs = {"user": f"uid={user},{ldap_domain.get_user_search_dn()}"}
            kwargs = {"user": user}
        kwargs["password"] = password
        return kwargs

    def get_user_info(self, connection, ldap_domain, user):
        user_info = {"user_dn": user}
        if not connection:
            return user_info
        usf = ldap_domain.get_user_search_filter() % {"user": user}
        user_search_dn = ldap_domain.get_user_search_dn()
        self.logger.debug("User search from %s: %s", user_search_dn, usf)
        connection.search(
            user_search_dn,
            usf,
            ldap3.SUBTREE,
            attributes=ldap_domain.get_user_search_attributes(),
        )
        if not connection.entries:
            self.logger.info("Cannot find user %s", user)
            return user_info
        entry = connection.entries[0]
        attrs = entry.entry_attributes_as_dict
        self.logger.debug("User attributes: %s", attrs if attrs else "No attributes response")
        user_info["user_dn"] = entry.entry_dn
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
        self.logger.debug("Group search from %s: %s", group_search_dn, gsf)
        connection.search(group_search_dn, gsf, ldap3.SUBTREE, attributes=["cn"])
        self.logger.debug("Groups found: %s", [e.entry_dn for e in connection.entries])
        return [e.entry_dn for e in connection.entries]
