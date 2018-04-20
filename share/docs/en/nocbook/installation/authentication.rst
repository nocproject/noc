Authentication
**************

Overview
========
NOC Supports pluggable authentication backends, allowing to authenticate users agains various sources.
Authentication source set up in ``etc/noc.conf:[authentication]/method``

Local Authentication
====================
Local authentication method stores all user credentials directly in NOC database. Local
authentication is the simplest method and require no additional configuration

HTTP Authentication
===================
HTTP Authentication rely on REMOTE_USER variable, delegating all details of authentication process
to the HTTP-server. You can use any authentication method, supported by webserver. To set up
HTTP authentication change [authentication] settings of etc/noc.conf to::

    method = http


LDAP Authentication
===================
LDAP authentication allows to authenticate users against enterprise LDAP or Active Directory database.

To set up LDAP authentication you need to install *python-ldap* package (does not provided in contrib/).
Next you need:

* LDAP server URL
* Bind method for LDAP (only *simple* is supported for now)
* To decide, will NOC use anonymous bind to lookup user, or will use *technical DN*
* To decide, will all directory users will have access to NOC, or restrict access only to one group
* Separate group to distinguish super-users

Then set up [authentication] settings of etc/noc.conf

Set authentication method to LDAP::

    method = ldap

Set up LDAP server url::

    ldap_server = ldap://ldap.example.com/
    
If your ldap server requires to specify partition, place it in the path::

    ldap_server = ldap://ldap.example.com/ou=noproject,ou=org

Set up bind method::

    ldap_bind_method = simple

If you decided to use *technical DN* set::

    ldap_bind_dn = cn=NOC User,ou=Users,ou=nocproject,ou=org
    ldap_bind_password = my_password

Set top of users tree::

    ldap_users_base = ou=Users,ou=nocproject,ou=org

Set up superusers group::

    ldap_superuser_group = cn=NOC Superusers,ou=Groups,ou=nocproject,ou=org

If you wish to allow only users of group (cn=NOC,ou=Group,ou=nocproject,ou=org) to access the NOC::

    ldap_required_group = cn=NOC,ou=Group,ou=nocproject,ou=org

This is enough to most installations. Sometimes, you need to adjust the search filter.
There is three search filters available 

* *ldap_users_filter* - Search for username, beginning from *ldap_users_base*
* *ldap_required_filter* - Search for user DN in *ldap_required_group*
* *ldap_superuser_filter* - Search for user DN in *ldap_superuser_group*

LDAP search bases and filters can hold any valid Django template to customize the search process according to your needs.
Refer to "The template layer" part of Django's documentation for template syntax and filters available.

Following variables can be used in templates. All variables are properly quoted and can be used in filters directly:

============ ==========================================================================
username     User name, as entered into login box
user         Left part from @ symbol (if found), or username
domain       Right part from @ symbol (if found), or not defined
domain_parts A list of domain parts (i.e ['nocproject','org'] for nocproject.org)
dn           user's DN, resolved against Users tree
============ ==========================================================================

Examples::

    ldap_required_filter = (|(uniqueMember={{dn}})(member={{user}}))
    ldap_users_filter = (&(objectClass=inetOrgPerson)(uid={{user}}))
    ldap_users_base = ou=Users{% for p in domain_parts %},ou={{p}}{% endfor %}
    ldap_users_base = ou={{p.0}},ou=Users,ou=nocproject,ou=org

