# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Test matcher
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.matcher import match


def test_zero():
    assert match({}, {}) == True
    assert match({"k", "v"}, {}) == True


def test_eq():
    assert match({"x": "y"}, {"x": "y"}) == True


def test_eq_and():
    assert match({"x": "y", "m": "n"}, {"x": "y", "m": "k"}) == False
    assert match({"x": "y", "m": "n"}, {"x": "y", "m": "n"}) == True


def test_regex():
    assert match({
        "platform": "S50N",
        "vendor": "Force10"
    }, {
        "platform": {
            "$regex": "^S"
        }
    }) == True
    assert match({
        "platform": "E600",
        "vendor": "Force10"
    }, {
        "platform": {
            "$regex": "^S"
        }
    }) == False
    assert match({
        "platform": "S50N",
        "vendor": "Force10"
    }, {
        "platform": {
            "$regex": "^S"
        },
        "vendor": "Force10"
    }) == True
    assert match({
        "platform": "S50N",
        "vendor": "Force10"
    }, {
        "platform": {
            "$regex": "^S"
        },
        "vendor": "Dell"
    }) == False


def test_in():
    assert match({
        "platform": "S50N",
        "vendor": "Force10"
    }, {
        "platform": {
            "$in": ["S50N", "S50P"]
        }
    }) == True
    assert match({
        "platform": "S50N",
        "vendor": "Force10"
    }, {
        "platform": {
            "$in": ["S50N", "S50P"]
        },
        "vendor": {
            "$in": ["Force10", "Dell"]
        }
    }) == True
    assert match({
        "platform": "S25N",
        "vendor": "Force10"
    }, {
        "platform": {
            "$in": ["S50N", "S50P"]
        }
    }) == False


def test_gt():
    assert match({
        "version": "12.2(50)SE"
    }, {
        "version": {
            "$gt": "12.2(48)SE"
        }
    }) == True
    assert match({
        "version": "12.2(50)SE"
    }, {
        "version": {
            "$gt": "12.2(50)SE"
        }
    }) == False
    assert match({
        "version": "12.2(50)SE"
    }, {
        "version": {
            "$gt": "12.2(51)SE"
        }
    }) == False


def test_gte():
    assert match({
        "version": "12.2(50)SE"
    }, {
        "version": {
            "$gte": "12.2(48)SE"
        }
    }) == True
    assert match({
        "version": "12.2(50)SE"
    }, {
        "version": {
            "$gte": "12.2(50)SE"
        }
    }) == True
    assert match({
        "version": "12.2(50)SE"
    }, {
        "version": {
            "$gte": "12.2(51)SE"
        }
    }) == False


def test_lt():
    assert match({
        "version": "12.2(50)SE"
    }, {
        "version": {
            "$lt": "12.2(48)SE"
        }
    }) == False
    assert match({
        "version": "12.2(50)SE"
    }, {
        "version": {
            "$lt": "12.2(50)SE"
        }
    }) == False
    assert match({
        "version": "12.2(50)SE"
    }, {
        "version": {
            "$lt": "12.2(51)SE"
        }
    }) == True


def test_lte():
    assert match({
        "version": "12.2(50)SE"
    }, {
        "version": {
            "$lte": "12.2(48)SE"
        }
    }) == False
    assert match({
        "version": "12.2(50)SE"
    }, {
        "version": {
            "$lte": "12.2(50)SE"
        }
    }) == True
    assert match({
        "version": "12.2(50)SE"
    }, {
        "version": {
            "$lte": "12.2(51)SE"
        }
    }) == True


def test_between():
    assert match({
        "version": "12.2(33)SE"
    }, {
        "version": {
            "$gte": "12.2(48)SE",
            "$lte": "12.2(52)SE"
        }
    }) == False
    assert match({
        "version": "12.2(48)SE"
    }, {
        "version": {
            "$gte": "12.2(48)SE",
            "$lte": "12.2(52)SE"
        }
    }) == True
    assert match({
        "version": "12.2(50)SE"
    }, {
        "version": {
            "$gte": "12.2(48)SE",
            "$lte": "12.2(52)SE"
        }
    }) == True
    assert match({
        "version": "12.2(52)SE"
    }, {
        "version": {
            "$gte": "12.2(48)SE",
            "$lte": "12.2(52)SE"
        }
    }) == True
    assert match({
        "version": "12.2(60)SE"
    }, {
        "version": {
            "$gte": "12.2(48)SE",
            "$lte": "12.2(52)SE"
        }
    }) == False
