# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Access control
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.db.models import Q
import noc.main.models
##
class PermissionDenied(Exception): pass
##
## Basic Permission class.
## Each permission must implement ``check`` method
## and additional queryset method
##
class Permission(object):
    def __init__(self):
        self.app=None
    ##
    ## Must return Q object restricting the list of available objects
    ##
    def queryset(self,request):
        return Q()
    ##
    ## Called to check wrether user has access
    ## For granular permissions obj=None means check user has application access
    ##
    def check(self,app,user,obj=None):
        raise Exception("Not implemented")
    ##
    ## Return human-readable representation of permission set
    ## Applicable only for granular permissions
    ##
    def display(self,user):
        return ""
    ##
    def __or__(self,r):
        return ORPermission(self,r)
    ##
    def __and__(self,r):
        return ANDPermission(self,r)
##
## Boolean logic permission
##
class LogicPermision(Permission):
    def __init__(self,l,r):
        super(Permission,self).__init__()
        self.l=l
        self.r=r
##
## Permit if left or right part permit
##
class ORPermission(LogicPermision):
    def check(self,app,user,obj=None):
        return self.l.check(app,user,obj) or self.r.check(app,user,obj)
    def queryset(self,request):
        return self.l.queryset(request)|self.r.queryset(request)
##
## Permit if left and right part permit
##
class ANDPermission(LogicPermision):
    def check(self,app,user,obj=None):
        return self.l.check(app,user,obj) and self.r.check(app,user,obj)
    def queryset(self,request):
        return self.l.queryset(request)&self.r.queryset(request)
##
## Permit access
##
class Permit(Permission):
    def check(self,app,user,obj=None):
        return True
##
## Deny access
##
class Deny(Permission):
    def check(self,app,user,obj=None):
        return False
##
## Permit access to logged users
##
class PermitLogged(Permission):
    def check(self,app,user,obj=None):
        return user.is_authenticated()
##
## Permit access to superusers
##
class PermitSuperuser(Permission):
    def check(self,app,user,obj=None):
        return user.is_superuser
##
## Permit access if user has permission ``perm``
##
class HasPerm(Permission):
    def __init__(self,perm):
        super(HasPerm,self).__init__()
        self.perm=perm
    
    def __repr__(self):
        if hasattr(self,"perm_id"):
            return "<HasPerm '%s' object at 0x%x>"%(self.perm_id,id(self))
        else:
            return "<HasPerm object at 0x%x>"%id(self)
    
    def get_permission(self,app):
        if ":" in self.perm:
            return self.perm
        else:
            return "%s:%s:%s"%(app.module,app.app,self.perm)

    def check(self,app,user,obj=None):
        return noc.main.models.Permission.has_perm(user,self.get_permission(app))
