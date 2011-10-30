# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Unittests for local authentication method
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
from noc.main.auth.backends.localbackend import NOCLocalBackend
from noc.lib.test import NOCTestCase


class LocalBackendTestCase(NOCTestCase):
    def setUp(self):
        User = NOCLocalBackend.User
        u = User(username="local_test", is_active=True, is_superuser=False)
        u.set_password("local_test")
        u.save()

    def test_get_user(self):
        backend = NOCLocalBackend()
        user = backend.User.objects.get(username="local_test")
        r = backend.get_user(user.id)
        self.assertNotEqual(r, None)
        self.assertEqual(r.username, "local_test")
        self.assertEqual(r.is_active, True)
        self.assertEqual(r.is_superuser, False)
        r = backend.get_user(1278221)
        self.assertEqual(r, None)

    def test_authenticate(self):
        backend = NOCLocalBackend()
        # Valid user, valid password
        r = backend.authenticate(username="local_test", password="local_test")
        self.assertNotEqual(r, None)
        self.assertEqual(r.username, "local_test")
        self.assertEqual(r.is_active, True)
        self.assertEqual(r.is_superuser, False)
        # Valid user, invalid password
        r = backend.authenticate(username="local_test", password="local_test1")
        self.assertEqual(r, None)
        # Invalid user, valid password
        r = backend.authenticate(username="local_test1", password="local_test")
        self.assertEqual(r, None)
        # Invalid user, invalid password
        r = backend.authenticate(username="local_test1", password="local_test1")
        self.assertEqual(r, None)

    def test_change_credentials(self):
        backend = NOCLocalBackend()
        user = backend.User.objects.get(username="local_test")
        # Failed attempt
        with self.assertRaises(ValueError):
            backend.change_credentials(user, old_password="l", new_password="1",
                                       retype_password="1")
        r = backend.authenticate(username="local_test", password="local_test")
        self.assertNotEqual(r, None)
        r = backend.authenticate(username="local_test", password="1")
        self.assertEqual(r, None)
        # Failed attempt #2
        with self.assertRaises(ValueError):
            backend.change_credentials(user, old_password="local_test",
                                       new_password="1", retype_password="2")
        r = backend.authenticate(username="local_test", password="local_test")
        self.assertNotEqual(r, None)
        r = backend.authenticate(username="local_test", password="1")
        self.assertEqual(r, None)
        # Success
        backend.change_credentials(user, old_password="local_test",
                                   new_password="1", retype_password="1")
        r = backend.authenticate(username="local_test", password="local_test")
        self.assertEqual(r, None)
        r = backend.authenticate(username="local_test", password="1")
        self.assertNotEqual(r, None)

    def test_get_or_create(self):
        backend = NOCLocalBackend()
        # Get existing
        r = backend.get_or_create_db_user("local_test", first_name="Local",
                                          last_name="Test")
        self.assertNotEqual(r, None)
        self.assertEqual(r.username, "local_test")
        self.assertEqual(r.is_active, True)
        self.assertEqual(r.is_superuser, False)
        self.assertEqual(r.first_name, "Local")
        self.assertEqual(r.last_name, "Test")
        # Create
        r = backend.get_or_create_db_user("local_test1", first_name="New",
                                          last_name="User", is_active=True,
                                          is_superuser=True,
                                          email="test@example.com")
        self.assertNotEqual(r, None)
        self.assertEqual(r.username, "local_test1")
        self.assertEqual(r.is_active, True)
        self.assertEqual(r.is_superuser, True)
        self.assertEqual(r.first_name, "New")
        self.assertEqual(r.last_name, "User")
        self.assertEqual(r.email, "test@example.com")
        r.delete()
