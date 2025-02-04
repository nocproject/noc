# ----------------------------------------------------------------------
# Password utilities tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from types import TracebackType

# Third-party modules
import pytest

# NOC modules
from noc.core.password.check import (
    check_password_policy,
    _check_len,
    _check_uppercase,
    _check_lowercase,
    _check_numbers,
    _check_specials,
    _check_history,
)
from noc.core.password.hasher import check_password, must_change, BaseHasher, make_password

# password
PW_HASH = "pbkdf2_sha256$600000$kna0TW8uWDQ0TtTPEJUd5l$rEruK5HNq9ngjTVcW2G8Vz/Pp+LKjpDoejtQZrYeD6U="
# password1
PW1_HASH = (
    "pbkdf2_sha256$600000$rbW00Slwr0LR6Ebv8bnjts$Li3Yo6b23Gz3tD3/T8pD88z36pg3KOPMGkZcJyrrL9g="
)


@pytest.mark.parametrize(
    ("password", "encoded"),
    [
        # Unsalted md5
        ("password", "5f4dcc3b5aa765d61d8327deb882cf99"),
        ("password", "md5$$5f4dcc3b5aa765d61d8327deb882cf99"),
        # Salted MD5
        ("password", "md5$aHQeQdpo8n59DXkTqnOR8V$476f71afaea0dcc9c38b83b898e52302"),
        # Unsalted SHA1
        ("password", "sha1$$5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8"),
        # Salted SHA1
        ("password", "sha1$REHsJBtjSlKMqw2zrMbjLp$21ac8f5dd28f99af14db89c28916211af2fcb2d8"),
        # Pbkdf2
        (
            "password",
            "pbkdf2_sha256$600000$kna0TW8uWDQ0TtTPEJUd5l$rEruK5HNq9ngjTVcW2G8Vz/Pp+LKjpDoejtQZrYeD6U=",
        ),
    ],
)
def test_check_password(password: str, encoded: str) -> None:
    assert check_password(password, encoded) is True


class ErrContext(object):
    def __init__(self, msg: str | None = None):
        self._msg = msg

    def __enter__(self) -> "ErrContext":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        if self._msg is None and exc_type is None:
            return
        if self._msg and exc_type is ValueError:
            assert self._msg == exc_val.args[0]
            return True


@pytest.mark.parametrize(
    ("password", "limit", "err"),
    [
        ("", 0, None),
        ("", None, None),
        ("a", 2, "Password too short. Must be 2 characters or longer"),
        ("aa", 2, None),
    ],
)
def test_check_len(password: str, limit: int | None, err: str | None) -> None:
    with ErrContext(err):
        _check_len(password, limit)


@pytest.mark.parametrize(
    ("password", "limit", "err"),
    [
        ("", 0, None),
        ("", None, None),
        ("a", 2, "Password must have at least 2 upper-case letters"),
        ("aa", 2, "Password must have at least 2 upper-case letters"),
        ("aA", 2, "Password must have at least 2 upper-case letters"),
        ("AA", 2, None),
    ],
)
def test_check_uppercase(password: str, limit: int | None, err: str | None) -> None:
    with ErrContext(err):
        _check_uppercase(password, limit)


@pytest.mark.parametrize(
    ("password", "limit", "err"),
    [
        ("", 0, None),
        ("", None, None),
        ("a", 2, "Password must have at least 2 lower-case letters"),
        ("AA", 2, "Password must have at least 2 lower-case letters"),
        ("aA", 2, "Password must have at least 2 lower-case letters"),
        ("aa", 2, None),
    ],
)
def test_check_lowercase(password: str, limit: int | None, err: str | None) -> None:
    with ErrContext(err):
        _check_lowercase(password, limit)


@pytest.mark.parametrize(
    ("password", "limit", "err"),
    [
        ("", 0, None),
        ("", None, None),
        ("a", 2, "Password must have at least 2 numbers"),
        ("A1", 2, "Password must have at least 2 numbers"),
        ("12", 2, None),
        ("12a", 2, None),
    ],
)
def test_check_numbers(password: str, limit: int | None, err: str | None) -> None:
    with ErrContext(err):
        _check_numbers(password, limit)


@pytest.mark.parametrize(
    ("password", "limit", "err"),
    [
        ("", 0, None),
        ("", None, None),
        ("a", 2, "Password must have at least 2 special symbols"),
        ("A@", 2, "Password must have at least 2 special symbols"),
        ("ab@c#", 2, None),
    ],
)
def test_check_specials(password: str, limit: int | None, err: str | None) -> None:
    with ErrContext(err):
        _check_specials(password, limit)


@pytest.mark.parametrize(
    ("password", "history", "err"),
    [
        ("password", None, None),
    ],
)
def test_check_history(password: str, history: list[str] | None, err: str | None) -> None:
    with ErrContext(err):
        _check_history(password, history)


@pytest.mark.parametrize(
    ("password", "config", "err"),
    [
        ("", {}, None),
        ("1", {"min_password_len": 2}, "Password too short. Must be 2 characters or longer"),
        (
            "1",
            {"min_password_len": 2, "min_password_uppercase": 2},
            "Password too short. Must be 2 characters or longer",
        ),
        ("12", {"min_password_len": 2}, None),
        (
            "12",
            {"min_password_len": 2, "min_password_uppercase": 2},
            "Password must have at least 2 upper-case letters",
        ),
        (
            "AB",
            {"min_password_len": 2, "min_password_uppercase": 2},
            None,
        ),
        (
            "Ab",
            {"min_password_len": 2, "min_password_lowercase": 2},
            "Password must have at least 2 lower-case letters",
        ),
        (
            "ab",
            {"min_password_len": 2, "min_password_lowercase": 2},
            None,
        ),
        (
            "ab",
            {"min_password_len": 2, "min_password_numbers": 2},
            "Password must have at least 2 numbers",
        ),
        (
            "A1",
            {"min_password_len": 2, "min_password_numbers": 2},
            "Password must have at least 2 numbers",
        ),
        ("12", {"min_password_len": 2, "min_password_numbers": 2}, None),
        ("12a", {"min_password_len": 2, "min_password_numbers": 2}, None),
        (
            "1#",
            {"min_password_len": 2, "min_password_specials": 2},
            "Password must have at least 2 special symbols",
        ),
        ("12@x#", {"min_password_len": 2, "min_password_specials": 2}, None),
        # History
        (
            "password",
            {
                "history": [
                    "md5$$5f4dcc3b5aa765d61d8327deb882cf98",
                    "md5$$5f4dcc3b5aa765d61d8327deb882cf99",
                ]
            },
            "Password is already used",
        ),
    ],
)
def test_password_policy(password: str, config: dict[str, int], err: str | None) -> None:
    with ErrContext(err):
        check_password_policy(password, **config)


def test_invalid_hasher() -> None:
    r = check_password("password", "invalid$$")
    assert r is False


@pytest.mark.parametrize(
    ("encoded", "expected"),
    [
        # Unsalted md5
        ("5f4dcc3b5aa765d61d8327deb882cf99", True),
        ("md5$$5f4dcc3b5aa765d61d8327deb882cf99", True),
        # Salted MD5
        ("md5$aHQeQdpo8n59DXkTqnOR8V$476f71afaea0dcc9c38b83b898e52302", True),
        # Unsalted SHA1
        ("sha1$$5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8", True),
        # Salted SHA1
        ("sha1$REHsJBtjSlKMqw2zrMbjLp$21ac8f5dd28f99af14db89c28916211af2fcb2d8", True),
        # Pbkdf2
        (
            "pbkdf2_sha256$60000$kna0TW8uWDQ0TtTPEJUd5l$rEruK5HNq9ngjTVcW2G8Vz/Pp+LKjpDoejtQZrYeD6U=",
            True,
        ),
        (
            "pbkdf2_sha256$600000$kna0TW8uWDQ0TtTPEJUd5l$rEruK5HNq9ngjTVcW2G8Vz/Pp+LKjpDoejtQZrYeD6U=",
            False,
        ),
        # Invalid hash
        ("invalid$$", True),
    ],
)
def test_must_change(encoded: str, expected: bool) -> None:
    r = must_change(encoded)
    assert r is expected


def test_base_must_change() -> None:
    r = BaseHasher.must_change("")
    assert r is False


def test_base_is_valid_hash() -> None:
    r = BaseHasher.is_valid_hash("")
    assert r is False


def test_base_encode() -> None:
    with pytest.raises(NotImplementedError):
        BaseHasher.encode("password")


def test_base_verify() -> None:
    with pytest.raises(NotImplementedError):
        BaseHasher.verify("password", "123")


def test_unknown_alg() -> None:
    with pytest.raises(ValueError):
        BaseHasher.get_hasher("123")


def test_make_password() -> None:
    password = "password"
    r_hash = make_password(password)
    assert r_hash, "Hash is empty"
    assert must_change(r_hash) is False, "Hash must be changed immediately"
    assert check_password(password, r_hash) is True, "Hash must be checkable"
