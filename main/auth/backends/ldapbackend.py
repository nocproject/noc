# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## LDAP Authentication backend
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import settings
import logging
import types
## Django modules
from django.template import Context, Template
## Third-party modules
try:
    import ldap
except ImportError:
    pass
## NOC modules
from base import NOCAuthBackend
from noc.settings import config


class NOCLDAPBackend(NOCAuthBackend):
    """
    LDAP Authentication backend
    """
    def __init__(self):
        super(NOCLDAPBackend, self).__init__()
        self.server = config.get("authentication", "ldap_server")
        self.bind_method = config.get("authentication", "ldap_bind_method")
        self.bind_dn = config.get("authentication", "ldap_bind_dn")
        self.bind_password = config.get("authentication", "ldap_bind_password")
        self.users_base = config.get("authentication", "ldap_users_base")
        self.users_filter = config.get("authentication", "ldap_users_filter")
        self.required_group = config.get("authentication",
                                         "ldap_required_group")
        self.requred_filter = config.get("authentication",
                                         "ldap_required_filter")
        self.superuser_group = config.get("authentication",
                                          "ldap_superuser_group")
        self.superuser_filter = config.get("authentication",
                                           "ldap_superuser_filter")

    def q(self, s):
        """
        LDAP quoting according to RFC2254
        """
        for c in "\*()\x00":
            s = s.replace(c, r"\%02x" % ord(c))
        return s

    def search_to_unicode(self, attrs):
        """
        Convert search attributes to unicode
        """
        a = {}
        for k, v in attrs.items():
            if type(v) == types.ListType:
                v = v[0]
            a[k] = unicode(v, "utf-8")
        return a

    def expand_template(self, template, context):
        """
        Expand template with context
        """
        r = Template(template).render(Context(context))
        logging.debug("LDAP: Expanding template: '%s' -> '%s'" % (template, r))
        return r

    def ldap_bind(self, client, username=None, password=None):
        """
        Bind client (simple mode)
        """
        if username is None and password is None:
            # Anonymous bind
            logging.debug("LDAP anonymous bind")
            client.simple_bind_s()
        else:
            # Bind according to bind methods
            if self.bind_method == "simple":
                logging.debug("LDAP simple bind to %s" % username)
                client.simple_bind_s(username, password)
            else:
                logging.error("Invalid ldap bind method: '%s'" % self.bind_method)
                raise ValueError("Invalid ldap bind method: '%s'" % self.bind_method)

    def authenticate(self, username=None, password=None, **kwargs):
        """
        Authenticate user against user and password
        """
        logging.debug("LDAP authenticatation: username=%s" % username)
        is_active = True  # User activity flag
        is_superuser = False  # Superuser flag
        # Prepare template context
        context = {
            "username": self.q(username),
            "user": self.q(username)
        }
        if "@" in username:
            u, d = username.split("@", 1)
            context["user"] = self.q(u)
            context["domain"] = self.q(d)
            context["domain_parts"] = [self.q(p) for p in d.split(".")]
        try:
            # Prepare LDAP client
            client = ldap.initialize(self.server)
            # Bind anonymously or with technical user to resolve username
            self.ldap_bind(client,
                self.bind_dn if self.bind_dn else None,
                self.bind_password if self.bind_password else None
                )
            # Search for user
            base = self.expand_template(self.users_base, context)
            filter = self.expand_template(self.users_filter, context)
            logging.debug("LDAP Search: filter: %s, base: %s" % (filter, base))
            ul = client.search_s(base, ldap.SCOPE_SUBTREE, filter,
                                 ["sn", "givenname", "mail"])
            if len(ul) == 0:
                # No user found
                logging.error("LDAP user lookup error. User '%s' is not found" % username)
                return None
            if len(ul) > 1:
                # Mistake in LDAP schema
                logging.error("LDAP schema error. More than one user returned for '%s'" % username)
                return None
            dn, attrs = ul[0]
            logging.debug("LDAP search returned: %s, %s" % (str(dn), str(attrs)))
            # Populate context with DN
            context["dn"] = dn
            # Try to authenticate
            client = ldap.initialize(self.server)
            self.ldap_bind(client, dn, password)
            # Check user is in required group
            if self.required_group:
                base = self.expand_template(self.required_group, context)
                filter = self.expand_template(self.requred_filter, context)
                logging.debug("LDAP checking user '%s' in group '%s'. filter: %s" % (dn, base, filter))
                ug = client.search_s(base, ldap.SCOPE_BASE, filter, [])
                is_active = len(ug) > 0
                if not is_active:
                    logging.debug("Disabling user '%s'" % username)
            # Check user is superuser
            if self.superuser_group:
                base = self.expand_template(self.superuser_group, context)
                filter = self.expand_template(self.superuser_filter, context)
                logging.debug("LDAP checking user '%s' in group '%s'. filter: %s" % (dn, base, filter))
                ug = client.search_s(base, ldap.SCOPE_BASE, filter, [])
                is_superuser = len(ug) > 0
                if is_superuser:
                    logging.debug("Granting superuser access to '%s'" % username)
        except ldap.LDAPError, why:
            logging.error("LDAP Error: %s" % str(why))
            return None
        logging.debug("LDAP user '%s' authenticated. User is %s" % (username,
                            {True: "active", False: "disabled"}[is_active]))
        attrs = self.search_to_unicode(attrs)
        # Successfull bind
        user = self.get_or_create_db_user(username=username,
                                          is_active=is_active,
                                          is_superuser=is_superuser,
                                          first_name=attrs.get("givenName"),
                                          last_name=attrs.get("sn"),
                                          email=attrs.get("mail"))
        # Authentication passed
        return user
