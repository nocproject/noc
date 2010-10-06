# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## LDAP Authentication backend
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.template import Context, Template
import settings,logging,types
## python-ldap library required
import ldap

##
## LDAP Authentication backend
##
class NOCLDAPBackend(ModelBackend):
    ##
    ## LDAP Quoting according to RFC2254
    ##
    def q(self,s):
        for c in "\*()\x00":
            s=s.replace(c,"\\%02x"%ord(c))
        return s
    ##
    ## Convert search attributes to unicode
    ##
    def search_to_unicode(self,attrs):
        a={}
        for k,v in attrs.items():
            if type(v)==types.ListType:
                v=v[0]
            a[k]=unicode(v,"utf-8")
        return a
    ##
    ## Expand template with context
    ##
    def expand_template(self,template,context):
        return Template(template).render(Context(context))
    ##
    ## Bind client
    ##
    def ldap_bind(self,client,username=None,password=None):
        if username is None and password is None:
            # Anonymous bind
            logging.debug("LDAP anonymous bind")
            client.simple_bind_s()
        else:
            # Bind according to bind methods
            if settings.AUTH_LDAP_BIND_METHOD=="simple":
                logging.debug("LDAP simple bind to %s"%username)
                client.simple_bind_s(username,password)
            else:
                logging.error("Invalid ldap bind method: '%s'"%settings.AUTH_LDAP_BIND_METHOD)
                raise Exception("Invalid ldap bind method: '%s'"%settings.AUTH_LDAP_BIND_METHOD)
    ##
    ## Get username and password and return a user
    ##
    def authenticate(self,username=None,password=None,**kwargs):
        is_active=True     # User activity flag
        is_superuser=False # Superuser flag
        # Prepare template context
        context={
            "username" : self.q(username),
            "user"     : self.q(username)
        }
        if "@" in username:
            u,d=username.split("@",1)
            context["user"]         = self.q(u)
            context["domain"]       = self.q(d)
            context["domain_parts"] = [self.q(p) for p in d.split(".")]
            
        try:
            # Prepare LDAP client
            client=ldap.initialize(settings.AUTH_LDAP_SERVER)
            # Bind anonymously or with technical user to resolve username
            self.ldap_bind(client,
                settings.AUTH_LDAP_BIND_DN if settings.AUTH_LDAP_BIND_DN else None,
                settings.AUTH_LDAP_BIND_PASSWORD if settings.AUTH_LDAP_BIND_PASSWORD else None
                )
            # Search for user
            base=self.expand_template(settings.AUTH_LDAP_USERS_BASE,context)
            filter=self.expand_template(settings.AUTH_LDAP_USERS_FILTER,context)
            logging.debug("LDAP Search: filter: %s, base: %s"%(filter,base))
            ul=client.search_s(base,ldap.SCOPE_SUBTREE,filter,["sn","givenname","mail"])
            if len(ul)==0:
                # No user found
                logging.error("LDAP user lookup error. User '%s' is not found"%username)
                return None
            if len(ul)>1:
                # Mistake in LDAP schema
                logging.error("LDAP schema error. More than one user returned for '%s'"%username)
                return None
            dn,attrs=ul[0]
            logging.debug("LDAP search returned: %s, %s"%(str(dn),str(attrs)))
            # Populate context with DN
            context["dn"]=dn
            # Try to authenticate
            client=ldap.initialize(settings.AUTH_LDAP_SERVER)
            self.ldap_bind(client,dn,password)
            # Check user is in required group
            if settings.AUTH_LDAP_REQUIRED_GROUP:
                base=self.expand_template(settings.AUTH_LDAP_REQUIRED_GROUP,context)
                filter=self.expand_template(settings.AUTH_LDAP_REQUIRED_FILTER,context)
                logging.debug("LDAP checking user '%s' in group '%s'. filter: %s"%(dn,base,filter))
                ug=client.search_s(base,ldap.SCOPE_BASE,filter,[])
                is_active=len(ug)>0
                if not is_active:
                    logging.debug("Disabling user '%s'"%username)
            # Check user is superuser
            if settings.AUTH_LDAP_SUPERUSER_GROUP:
                base=self.expand_template(settings.AUTH_LDAP_SUPERUSER_GROUP,context)
                filter=self.expand_template(settings.AUTH_LDAP_SUPERUSER_FILTER,context)
                logging.debug("LDAP checking user '%s' in group '%s'. filter: %s"%(dn,base,filter))
                ug=client.search_s(base,ldap.SCOPE_BASE,filter,[])
                is_superuser=len(ug)>0
                if is_superuser:
                    logging.debug("Granting superuser access to '%s'"%username)
        except ldap.LDAPError,why:
            logging.error("LDAP Error: %s"%str(why))
            return None
        logging.debug("LDAP user '%s' authenticated. User is %s"%(username,{True:"active",False:"disabled"}[is_active]))
        attrs=self.search_to_unicode(attrs)
        # Successfull bind
        user,created=User.objects.get_or_create(username=username)
        user.set_password(password)
        if created:
            logging.debug("Created user '%s'"%username)
        # Update user data and credentials
        if "givenName" in attrs:
            user.first_name=attrs["givenName"]
        if "sn" in attrs:
            user.last_name=attrs["sn"]
        if "mail" in attrs:
            user.email=attrs["mail"]
        user.is_staff=True
        user.is_active=is_active
        user.is_superuser=is_superuser
        logging.debug("Updating user '%s' credentials"%username)
        user.save()
        # Authentication passed
        return user
    ##
    ## 
    ##
    def get_user(self,user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
    