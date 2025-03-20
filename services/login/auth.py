# ---------------------------------------------------------------------
# Authentication handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
from typing import Optional, Any
import datetime

# Third-party modules
from jose import jwt, jwk
from fastapi.responses import Response

# NOC modules
from noc.aaa.models.user import User
from noc.config import config
from noc.core.perf import metrics
from noc.core.comp import smart_text
from noc.core.error import NOCError, ERR_AUTH_CRED_CHANGE
from .backends.loader import loader

logger = logging.getLogger(__name__)

# Fields excluded from logging
HIDDEN_FIELDS = {"password", "new_password", "old_password", "retype_password"}

# Build JWK for sign/verify
jwt_key = jwk.construct(config.secret_key, algorithm=config.login.jwt_algorithm).to_dict()


class ChangeCredentialsError(NOCError):
    default_code = ERR_AUTH_CRED_CHANGE


def iter_methods():
    for m in config.login.methods.split(","):
        yield m.strip()


def authenticate(credentials: dict[str, Any]) -> str | None:
    """
    Authenticate user. Returns username when user is authenticated
    """
    c = credentials.copy()
    for f in HIDDEN_FIELDS:
        if f in c:
            c[f] = "***"
    le = "No active auth methods"
    for method in iter_methods():
        bc = loader.get_class(method)
        if not bc:
            logger.error("Cannot initialize backend '%s'", method)
            continue
        backend = bc()
        logger.info("Authenticating credentials %s using method %s", c, method)
        try:
            user = backend.authenticate(**credentials)
            metrics["auth_try", ("method", method)] += 1
        except backend.LoginError as e:
            logger.info("[%s] Login Error: %s", method, smart_text(e))
            metrics["auth_fail", ("method", method)] += 1
            le = smart_text(e)
            continue
        logger.info("Authorized credentials %s as user %s", c, user)
        metrics["auth_success", ("method", method)] += 1
        return user
    logger.error("Login failed for %s: %s", c, le)
    return None


def register_last_login(user: str):
    if config.login.register_last_login:
        u = User.get_by_username(user)
        if u:
            u.register_login()


def get_jwt_token(user: str, expire: Optional[int] = None, audience: Optional[str] = None) -> str:
    """
    Build JWT token for given user
    :param user: User name
    :param expire: Expiration time in seconds
    :param aud: Token audience
    :return:
    """
    expire = expire or config.login.session_ttl
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=expire)
    payload = {
        "sub": user,
        "exp": exp,
    }
    if audience:
        payload["aud"] = audience
    return jwt.encode(payload, jwt_key, algorithm=config.login.jwt_algorithm)


def get_user_from_jwt(token: str, audience: Optional[str] = None) -> str:
    """
    Check JWT token and return user.
    Raise ValueError if failed
    :param token:
    :return:
    """
    try:
        token = jwt.decode(
            token, jwt_key, algorithms=[config.login.jwt_algorithm], audience=audience
        )
        user = None
        if isinstance(token, dict):
            user = token.get("sub")
            if audience and token.get("aud") != audience:
                raise ValueError("Invalid audience")
        if not user:
            raise ValueError("Malformed token")
        return user
    except jwt.ExpiredSignatureError:
        raise ValueError("Expired token")
    except jwt.JWTError as e:
        raise ValueError(str(e))


def get_exp_from_jwt(token: str, audience: Optional[str] = None) -> datetime:
    """
    Check JWT token and return exp.
    Raise ValueError if failed
    :param token:
    :param audience:
    :return:
    """
    try:
        token = jwt.decode(
            token, jwt_key, algorithms=[config.login.jwt_algorithm], audience=audience
        )
        exp = None
        if isinstance(token, dict):
            exp = token.get("exp")
        if not exp:
            raise ValueError("Malformed token")
        return exp
    except jwt.ExpiredSignatureError:
        raise ValueError("Expired token")
    except jwt.JWTError as e:
        raise ValueError(str(e))


def set_jwt_cookie(response: Response, user: str, /, expire: int | None = None) -> None:
    """
    Generate JWT token and append as cookie to response.

    Args:
        response: Response instance.
        user: User name.
    """
    expire = expire or config.login.session_ttl
    response.set_cookie(
        key=config.login.jwt_cookie_name,
        value=get_jwt_token(user, audience="auth", expire=expire),
        expires=expire,
    )


def change_credentials(credentials: dict[str, Any]) -> None:
    """
    Change credentials.

    Args:
        credentials: dict of credentials, method-dependent.

    Raises:
        ChangeCredentialsError: When unable to change credentials.
    """
    c = credentials.copy()
    for f in HIDDEN_FIELDS:
        if f in c:
            c[f] = "***"
    for method in iter_methods():
        bc = loader.get_class(method)
        if not bc:
            logger.error("Cannot initialize backend '%s'", method)
            continue
        backend = bc()
        logger.info("Changing credentials %s using method %s", c, method)
        try:
            backend.change_credentials(**credentials)
            logger.info("Changed user credentials: %s", c)
            return
        except NotImplementedError:
            continue
        except backend.LoginError as e:
            logger.error("Failed to change credentials for %s: %s", c, e)
            raise ChangeCredentialsError(e.args[0]) from e
