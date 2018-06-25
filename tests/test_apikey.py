# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# APIKey test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
# NOC modules
from noc.main.models.apikey import APIKey, APIAccess


def test_apikey_access_active():
    secret = "test_apikey_access_active"
    # Prepare key
    key = APIKey(
        name="key1",
        description="Non-expiring key",
        is_active=True,
        key=secret,
        access=[
            APIAccess(
                api="api1",
                role="*"
            ),
            APIAccess(
                api="api2",
                role="r1"
            ),
            APIAccess(
                api="api2",
                role="r2"
            )
        ]
    )
    key.save()
    # Check
    assert APIKey.get_access(secret) == [("api1", "*"), ("api2", "r1"), ("api2", "r2")]
    assert APIKey.get_access_str(secret) == "api1:*,api2:r1,api2:r2"
    # Cleanup
    key.delete()


def test_apikey_access_inactive():
    secret = "test_apikey_access_inactive"
    # Prepare key
    key = APIKey(
        name="key1",
        description="Non-expiring key, Inactive",
        is_active=False,
        key=secret,
        access=[
            APIAccess(
                api="api1",
                role="*"
            ),
            APIAccess(
                api="api2",
                role="r1"
            ),
            APIAccess(
                api="api2",
                role="r2"
            )
        ]
    )
    key.save()
    # Check
    assert APIKey.get_access(secret) == []
    assert APIKey.get_access_str(secret) == ""
    # Cleanup
    key.delete()


def test_apikey_access_non_expired():
    secret = "test_apikey_access_non_expired"
    # Prepare key
    key = APIKey(
        name="key1",
        description="Expiring key",
        expires=datetime.datetime(year=2050, month=1, day=1),
        is_active=True,
        key=secret,
        access=[
            APIAccess(
                api="api1",
                role="*"
            ),
            APIAccess(
                api="api2",
                role="r1"
            ),
            APIAccess(
                api="api2",
                role="r2"
            )
        ]
    )
    key.save()
    # Check
    assert APIKey.get_access(secret) == [("api1", "*"), ("api2", "r1"), ("api2", "r2")]
    assert APIKey.get_access_str(secret) == "api1:*,api2:r1,api2:r2"
    # Cleanup
    key.delete()


def test_apikey_access_expired():
    secret = "test_apikey_access_non_expired"
    # Prepare key
    key = APIKey(
        name="key1",
        description="Expiring key",
        expires=datetime.datetime.now(),
        is_active=True,
        key=secret,
        access=[
            APIAccess(
                api="api1",
                role="*"
            ),
            APIAccess(
                api="api2",
                role="r1"
            ),
            APIAccess(
                api="api2",
                role="r2"
            )
        ]
    )
    key.save()
    # Check
    assert APIKey.get_access(secret) == []
    assert APIKey.get_access_str(secret) == ""
    # Cleanup
    key.delete()


def test_apikey_invalid():
    secret = "no such key"
    assert APIKey.get_access(secret) == []
    assert APIKey.get_access_str(secret) == ""
