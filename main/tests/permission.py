# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Unittests for access system
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from unittest import TestCase
from noc.main.models import *
##
##
##
class AccessTestCase(TestCase):
    permissions=set(["mod1:app1:p1","mod1:app1:p2","mod1:app2:p1"])
    def setUp(self):
        User(username="superuser",is_active=True,is_superuser=True).save()
        User(username="disabled",is_active=False).save()
        User(username="user1",is_active=True).save()
        User(username="user2",is_active=True).save()
        User(username="user3",is_active=True).save()
        Group(name="group1").save()
        Group(name="group2").save()
        for p in self.permissions:
            Permission(name=p).save()
    
    def tearDown(self):
        for p in self.permissions:
            Permission.objects.get(name=p).delete()
        User.objects.get(username="superuser").delete()
        User.objects.get(username="disabled").delete()
        User.objects.get(username="user1").delete()
        User.objects.get(username="user2").delete()
        User.objects.get(username="user3").delete()
        Group.objects.get(name="group1").delete()
        Group.objects.get(name="group2").delete()
    
    def test_permissions(self):
        superuser=User.objects.get(username="superuser")
        user1=User.objects.get(username="user1")
        Permission.set_user_permissions(user1,self.permissions)
        self.assertEquals(Permission.get_user_permissions(user1),self.permissions)
        group1=Group.objects.get(name="group1")
        Permission.set_group_permissions(group1,self.permissions)
        self.assertEquals(Permission.get_group_permissions(group1),self.permissions)
        user2=User.objects.get(username="user2")
        user2.groups.add(group1)
        user3=User.objects.get(username="user3")
        disabled_user=User.objects.get(username="disabled")
        Permission.set_user_permissions(disabled_user,self.permissions)
        disabled_user.groups.add(group1)
        # Check permissions are set
        for p in self.permissions:
            self.assertEquals(Permission.has_perm(superuser,p),True) # Always true for superuser
            self.assertEquals(Permission.has_perm(disabled_user,p),False) # Always false for disabled user
            self.assertEquals(Permission.has_perm(user1,p),True)     # User permissions
            self.assertEquals(Permission.has_perm(user2,p),True)     # Group permissions
            self.assertEquals(Permission.has_perm(user3,p),False)    # Not set
        # Test revoking of permissions
        Permission.set_user_permissions(user1,set())
        self.assertEquals(Permission.get_user_permissions(user1),set([]))
        Permission.set_group_permissions(group1,set())
        self.assertEquals(Permission.get_group_permissions(group1),set([]))
    
    def testUnicode(self):
        for p in self.permissions:
            self.assertEquals(unicode(Permission.objects.get(name=p)),p)
