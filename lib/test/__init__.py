# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC Test Suite
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import os
import base64
import random
## Django modules
from django.test import TestCase
from django.core import serializers
from django.utils import unittest  # unittest2 backport
from django.test.client import Client, MULTIPART_CONTENT
from django.utils.http import urlencode
## NOC modules
from noc.lib.serialize import json_encode, json_decode
from noc.main.models import User, Permission


class TestClient(Client):
    """
    HTTP test client
    """
    def __init__(self, prefix=None, follow=False, credentials={},
                 nocache=None, json=False, *args, **kwargs):
        """
        Create test HTTP client
        :param prefix: URL path prefix
        :param follow: Auto-follow HTTP 3xx responses
        :type follow: bool
        :param credentials: User credentials with optional
                            _user_ and _password_ keys
        :type credentials: dict
        :param nocache: Generate query URL variable with random value for
                        every request
        :type nocache: str
        :param json: Auto-convert request and response data to JSON format
        :type json: bool
        """
        super(TestClient, self).__init__(*args, **kwargs)
        if prefix and prefix.endswith("/"):
            self.prefix = prefix[:-1]
        else:
            self.prefix = prefix
        self.follow = follow
        self.credentials = {}
        self.nocache = nocache
        self.json = json

    def to_follow(self, follow):
        return self.follow if follow is None else follow

    def get_path(self, path, query={}):
        """
        Generate effective URL path
        """
        if self.prefix:
            if path.startswith("/"):
                path = path[1:]
            path = "/".join([self.prefix, path])
        q = self.get_query(query)
        if q:
            path += "?" + urlencode(q, doseq=True)
        return path

    def get_query(self, query={}):
        """
        Generate dict with URL query variables
        :param query: dict containing variables for URL query
        :return: dict containing variables for URL query
        """
        q = query.copy()
        if self.nocache:
            q[self.nocache] = str(random.randint(0, 0x7FFFFFFF))
        return q

    def get_headers(self, headers={}, credentials={}):
        """
        Generate Basic HTTP headers
        :param headers: Dict containing HTTP Request headers
        :type headers: dict
        :param credentials: Dict containing optional _user_ and _password_ keys
        :type dict:
        :returns: Dict with HTTP headers
        :rtype: dict
        """
        h = headers.copy()
        if not credentials and self.credentials:
            credentials = self.credentials
        if credentials:
            ah = "%s:%s" % (credentials.get("user", ""),
                            credentials.get("password", ""))
            h["HTTP_AUTHORIZATION"] = "Basic %s" % base64.b64encode(ah)
        return h

    def get(self, path, query={}, credentials={}, follow=None, json=None,
            **extra):
        """
        HTTP GET Request
        :param path: URL path
        :param query: URL query
        :param credentials: Request credentials
        :param follow: Auto-follow HTTP 3xx responses. Use client-wide settings
                       if empty
        :param extra: Additional HTTP request headers
        """
        r = super(TestClient, self).get(self.get_path(path,
                  query=dict((k, str(query[k])) for k in query)),
                  follow=self.to_follow(follow),
                  **self.get_headers(headers=extra, credentials=credentials))
        return r

    def post(self, path, query={}, credentials={}, follow=None,
             content_type=MULTIPART_CONTENT, data={}, **extra):
        """
        HTTP POST Request
        :param path: URL path
        :param query: URL query
        :param credentials: Request credentials
        :param content_type: Request content-type
        :param data: POST data
        :param extra: Additional HTTP request headers
        """
        return super(TestClient, self).post(self.get_path(path, query=query),
                    data=data,
                    follow=self.to_follow(follow),
                    content_type=content_type,
                    **self.get_headers(headers=extra, credentials=credentials))

    def put(self, path, query={}, credentials={}, follow=None,
            content_type=MULTIPART_CONTENT, data={}, **extra):
        """
        HTTP PUT Request
        :param path: URL path
        :param query: URL query
        :param credentials: Request credentials
        :param content_type: Request content-type
        :param data: POST data
        :param extra: Additional HTTP request headers
        """
        return super(TestClient, self).put(self.get_path(path, query=query),
                    data=data,
                    follow=self.to_follow(follow),
                    content_type=content_type,
                    **self.get_headers(headers=extra, credentials=credentials))

    def delete(self, path, query={}, credentials={}, follow=None,
               data={}, **extra):
        """
        HTTP DELETE Request
        :param path: URL path
        :param query: URL query
        :param credentials: Request credentials
        :param data: POST data
        :param extra: Additional HTTP request headers
        """
        return super(TestClient, self).delete(self.get_path(path, query=query),
                    data=data,
                    follow=self.to_follow(follow),
                    **self.get_headers(headers=extra, credentials=credentials))


@unittest.skip("ApplicationTestCase is obsolete")
class ApplicationTestCase(TestCase):
    pass


@unittest.skip("ModelApplicationTestCase is obsolete")
class ModelApplicationTestCase(TestCase):
    pass


@unittest.skip("ReportApplicationTestCase is obsolete")
class ReportApplicationTestCase(TestCase):
    pass


class NOCTestCase(TestCase):
    """
    Base class for unittests
    """
    fixtures = []  # A list of texture files

    def __init__(self, methodName="runTest"):
        p = self.__class__.__module__.split(".")
        self.test_dir = None
        if p[0] == "noc":
            self.test_dir = os.path.sep.join(p[1:-1])
        super(NOCTestCase, self).__init__(methodName)

    def load_fixture(self, file):
        """
        Load canned objects from file
        """
        with open(os.path.join(self.test_dir, file)) as f:
            data = f.read()
        for o in serializers.deserialize("json", data):
            o.save()

    def setUp(self):
        """
        Prepare tests and load fixtures
        """
        super(NOCTestCase, self).setUp()  # Call test initialization
        # Load fixtures when given
        if self.test_dir and self.fixtures:
            for f in self.fixtures:
                self.load_fixture(f)


class ModelTestCase(NOCTestCase):
    """
    ORM Model test case
    """
    model = None  # Django ORM Model
    data = []  # List of field->value with test data

    def get_data(self):
        """
        Generator returning test data records for operations tests
        """
        for d in self.data:
            yield d

    def object_test(self, obj):
        """
        Additional object tests. Called for each test object created
        """
        pass

    def test_object_operations(self):
        """
        Test basic object creation, manipulation and removing
        """
        # Find unique fields
        unique_field = None
        for field in self.model._meta.fields:
            if field.unique and field.name != "id":
                unique_field = field.attname
                break
        # Find nullable fields
        null_fields = [f.attname for f in self.model._meta.fields if f.null]
        # Find related fields
        rel_fields = dict([(f.attname, f.rel.to)
            for f in self.model._meta.fields if f.rel])
        ## Unicode object labels.
        ## Check all objects generate unique labels
        unicodes = set()
        # Perform test loop
        for rd in self.get_data():
            # Resolve related objects
            for n in rd:
                if n in rel_fields:
                    rd[n[:-3]] = rel_fields[n].objects.get(id=rd[n])
                    del rd[n]
            # Create object
            o = self.model(**rd)
            o.save()
            # Test unicode
            u = unicode(o)
            self.assertNotIn(u, unicodes)  # Must be unique
            unicodes.add(u)
            # Find object
            if unique_field:
                ou = self.model.objects.get(**{unique_field: rd[unique_field]})
                self.assertEquals(o.id, ou.id)
            # Additional object tests
            self.object_test(o)
            # Reset nullable fields
            if null_fields:
                nfv = {}
                for f in null_fields:
                    nfv[f] = getattr(o, f)
                    setattr(o, f, None)
                o.save()
                # Restore values
                for f in nfv:
                    setattr(o, f, nfv[f])
                o.save()
            # Delete object
            o.delete()


class AjaxTestCase(NOCTestCase):
    app = None  # Application id (<module>.<name>)
    # Users to create
    # username -> {
    #     is_superuser: True|False
    #     permissions: []
    # }
    users = {}

    HTTP_OK = 200
    HTTP_CREATED = 201
    HTTP_FORBIDDEN = 403
    HTTP_NOT_FOUND = 404
    
    def setUp(self):
        super(AjaxTestCase, self).setUp()
        prefix = "/%s/" % self.app.replace(".", "/")
        self.client = TestClient(prefix=prefix, json=True, nocache="_dc")
        # Create users
        for user in self.users:
            d = self.users[user]
            u = User(username=user, is_staff=True,
                     is_superuser=d.get("is_superuser", False))
            u.set_password(user)
            u.save()
            # Set permissions
            perms = d.get("permissions")
            if perms:
                pprefix = self.app.replace(".", ":") + ":"
                pset = set()
                for p in perms:
                    if ":" not in p:
                        p = pprefix + p
                    pset.add(p)
                Permission.set_user_permissions(u, pset)

    def tearDown(self):
        super(AjaxTestCase, self).tearDown()
        User.objects.filter(username__in=self.users.keys()).delete()

    def request(self, method, path, user=None, **kwargs):
        if user is None:
            kwargs["credentials"] = {}
        else:
            kwargs["credentials"] = {"user": user, "password": user}
        # Convert input to JSON
        if "data" in kwargs:
            kwargs["data"] = json_encode(kwargs["data"])
            if method in ("post", "put"):
                kwargs["content_type"] = "text/json"
        r = getattr(self.client, method)(path, **kwargs)
        if r.has_header("Content-Type") and r["Content-Type"].startswith("text/json"):
            return (r.status_code,
                    json_decode(r.content))
        else:
            return r.status_code, r.content

    def get(self, path, **kwargs):
        return self.request("get", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("post", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("put", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("delete", path, **kwargs)

    def assertDictIn(self, a, b, msg=None):
        """
        Check all fields of dict a presents in b
        :param a: Dict of fields to check
        :type a: dict
        :param b: List or dict
        :type b: dict or list
        """
        def match(a, b):
            for f in a:
                if a[f] != b[f]:
                    return False
            return True
        
        if type(b) == dict:
            m = match(a, b)
        elif type(b) == list:
            m = False
            for c in b:
                if match(a, c):
                    m = True
                    break
        self.assertTrue(m, "%s not in %s" % (a, b))


class RestModelTestCase(AjaxTestCase):
    """
    Common CRUD application pattern
    
    """
    users = {
        "superuser": {"is_superuser": True},
        "create": {"permissions": ["create"]},
        "read": {"permissions": ["read"]},
        "update": {"permissions": ["update"]},
        "delete": {"permissions": ["delete"]}
    }

    scenario = []  # {GET, POST, PUT}

    def test_rest_superuser(self):
        """
        Test default REST operation as superuser
        Scenario is a list of {GET, POST, PUT}
        """
        for s in self.scenario:
            # Check object is not in database
            # Query for object
            status, data = self.get("/", user="superuser", query=s["GET"])
            self.assertEquals(status, self.HTTP_OK)
            self.assertEquals(data, [])
            # Lookup for object
            status, data = self.get("/lookup/", user="superuser", query=s["GET"])
            self.assertEquals(status, self.HTTP_OK)
            self.assertEquals(data, [])
            # Create object
            status, data = self.post("/", user="superuser", data=s["POST"])
            self.assertEquals(status, self.HTTP_CREATED)
            self.assertIn("id", data)  # Must return object's JSON
            self.assertDictIn(s["POST"], data)  # Must return object back
            object_id = data["id"]
            path = str(object_id)
            # Create duplicated object
            status, data = self.post("/", user="superuser", data=s["POST"])
            self.assertEquals(status, 409)
            # Get object
            status, data = self.get(path, user="superuser")
            self.assertEquals(status, self.HTTP_OK)
            self.assertIn("id", data)
            self.assertEquals(object_id, data["id"])
            # Lookup for object
            status, data = self.get("/lookup/", user="superuser",
                                    query={"id": object_id})
            self.assertEquals(status, self.HTTP_OK)
            self.assertDictIn({"id": object_id}, data)
            self.assertEquals(len(data), 1)
            # Get objects list
            status, data = self.get("/", user="superuser")
            self.assertEquals(status, self.HTTP_OK)
            self.assertDictIn(s["POST"], data)
            # Get paged objects list (ExtJS format)
            query = {
                "__format": "ext",
                "__limit": 10,
                "__start": 0,
                "__page": 0
            }
            query.update(s["POST"])
            status, data = self.get("/", user="superuser",
                                    query=query)
            self.assertEquals(status, self.HTTP_OK)
            self.assertIn("total", data)
            self.assertIn("success", data)
            self.assertIn("data", data)
            self.assertEquals(data["success"], True)
            self.assertDictIn(s["POST"], data["data"])
            # Change
            status, data = self.put(path, user="superuser", data=s["PUT"])
            self.assertEquals(status, self.HTTP_OK)
            # Get and check updates
            status, data = self.get(path, user="superuser")
            self.assertEquals(status, self.HTTP_OK)
            self.assertDictIn(s["PUT"], data)
            # Delete
            status, data = self.delete(path, user="superuser")
            self.assertEquals(status, 204)
            # Check object is not available
            status, data = self.get(path, user="superuser")
            self.assertEquals(status, self.HTTP_NOT_FOUND)
            # Try to PUT deleted object and get 404
            status, data = self.put(path, user="superuser", data=s["PUT"])
            self.assertEquals(status, self.HTTP_NOT_FOUND)
            # Try to delete again and get 404
            status, data = self.delete(path, user="superuser")
            self.assertEquals(status, self.HTTP_NOT_FOUND)

    def test_rest_user(self):
        """
        Test default REST operations as users with different permissions
        Scenario is a list of {GET, POST, PUT}
        """
        # Users
        users = [u for u in self.users if "is_superuser" not in self.users[u]]
        for s in self.scenario:
            # Check object is not in database
            # Query for object
            for u in users:
                status, data = self.get("/", user=u, query=s["GET"])
                if u == "read":
                    self.assertEquals(status, self.HTTP_OK)
                    self.assertEquals(data, [])
                else:
                    self.assertEquals(status, self.HTTP_FORBIDDEN)
            # Create object
            for u in users:
                status, data = self.post("/", user=u, data=s["POST"])
                if u == "create":
                    self.assertEquals(status, self.HTTP_CREATED)
                    self.assertIn("id", data)  # Must return object's JSON
                    self.assertDictIn(s["POST"], data)  # Must return object back
                    object_id = data["id"]
                    path = str(object_id)
                else:
                    self.assertEquals(status, self.HTTP_FORBIDDEN)
            # Create duplicated object
            for u in users:
                status, data = self.post("/", user=u, data=s["POST"])
                if u == "create":
                    self.assertEquals(status, 409)
                else:
                    self.assertEquals(status, self.HTTP_FORBIDDEN)
            # Get object
            for u in users:
                status, data = self.get(path, user=u)
                if u == "read":
                    self.assertEquals(status, self.HTTP_OK)
                    self.assertIn("id", data)
                    self.assertEquals(object_id, data["id"])
                else:
                    self.assertEquals(status, self.HTTP_FORBIDDEN)
            # Get objects list
            for u in users:
                status, data = self.get("/", user=u)
                if u == "read":
                    self.assertDictIn(s["POST"], data)
                else:
                    self.assertEquals(status, self.HTTP_FORBIDDEN)
            # Change
            for u in users:
                status, data = self.put(path, user=u, data=s["PUT"])
                if u == "update":
                    self.assertEquals(status, self.HTTP_OK)
                else:
                    self.assertEquals(status, self.HTTP_FORBIDDEN)
            # Get and check updates
            for u in users:
                status, data = self.get(path, user=u)
                if u == "read":
                    self.assertEquals(status, self.HTTP_OK)
                    self.assertDictIn(s["PUT"], data)
                else:
                    self.assertEquals(status, self.HTTP_FORBIDDEN)
            # Delete
            for u in users:
                status, data = self.delete(path, user=u)
                if u == "delete":
                    self.assertEquals(status, 204)
                else:
                    self.assertEquals(status, self.HTTP_FORBIDDEN)
            # Check object is not available
            for u in users:
                status, data = self.get(path, user=u)
                if u == "read":
                    self.assertEquals(status, self.HTTP_NOT_FOUND)
                else:
                    self.assertEquals(status, self.HTTP_FORBIDDEN)
            # Try to PUT deleted object
            for u in users:
                status, data = self.put(path, user=u, data=s["PUT"])
                if u == "update":
                    self.assertEquals(status, self.HTTP_NOT_FOUND)
                else:
                    self.assertEquals(status, self.HTTP_FORBIDDEN)

            # Try to delete again and get 404
            for u in users:
                status, data = self.delete(path, user=u)
                if u == "delete":
                    self.assertEquals(status, self.HTTP_NOT_FOUND)
                else:
                    self.assertEquals(status, self.HTTP_FORBIDDEN)

from noc.lib.test.scripttestcase import ScriptTestCase
