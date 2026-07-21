# ----------------------------------------------------------------------
# /api/auth/auth/ handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import codecs
from urllib.parse import quote

# Third-party modules
from fastapi import APIRouter, Request, Cookie, Header, Depends
from fastapi.responses import JSONResponse
import cachetools

# NOC modules
from noc.config import config
from noc.aaa.models.apikey import APIKey
from noc.core.comp import smart_bytes
from ..auth import (
    authenticate,
    register_last_login,
    set_jwt_cookie,
    get_user_from_jwt,
    get_user_from_cert_subject,
)
from noc.core.service.deps.service import get_service
from noc.services.login.service import LoginService

router = APIRouter()
logger = logging.getLogger(__name__)

PINHOLE_PATHS = {
    "/api/login/login",
    "/api/login/is_logged",
    "/api/login/token",
    "/api/zeroconf/config",
    "/api/metricscollector/send",
}


def encode_user(user: str) -> str:
    """
    Encode username to be passed via Remote-User.

    Args:
        user: User name.

    Returns:
        encoded user name.
    """
    return quote(user)


@router.get("/api/auth/auth/", tags=["auth"])
@router.post("/api/auth/auth/", tags=["auth"])
@router.put("/api/auth/auth/", tags=["auth"])
@router.head("/api/auth/auth/", tags=["auth"])
@router.delete("/api/auth/auth/", tags=["auth"])
@router.options("/api/auth/auth/", tags=["auth"])
@router.patch("/api/auth/auth/", tags=["auth"])
@router.trace("/api/auth/auth/", tags=["auth"])
async def auth(
    request: Request,
    jwt_cookie: str | None = Cookie(None, alias=config.login.jwt_cookie_name),
    private_token: str | None = Header(None, alias="Private-Token"),
    authorization: str | None = Header(None, alias="Authorization"),
    original_uri: str | None = Header(None, alias="X-Original-URI"),
    remote_cert_subj: str | None = Header(None, alias="X-Remote-Cert-Subject"),
    svc: LoginService = Depends(get_service),
):
    """
    Authenticate request. Called via nginx's auth_proxy
    """
    if original_uri and is_pinhole(original_uri):
        # Pinholes to endpoints without authorization
        return JSONResponse({"status": True}, status_code=200)
    if remote_cert_subj:
        cert_user = get_user_from_cert_subject(remote_cert_subj)
        logger.info("Remote party certificate subject: %s", remote_cert_subj)
        logger.info("Pinning to user %s", cert_user)
    else:
        cert_user = None
    if jwt_cookie:
        return await auth_cookie(request=request, jwt_cookie=jwt_cookie, pinned_user=cert_user)
    if private_token:
        return await auth_private_token(
            request=request, private_token=private_token, pinned_user=cert_user
        )
    if authorization:
        return await auth_authorization(
            request=request, authorization=authorization, svc=svc, pinned_user=cert_user
        )
    logger.error("[%s] Denied: Unsupported authentication method", request.client.host)
    return JSONResponse({"status": False}, status_code=401)


async def auth_cookie(
    request: Request, jwt_cookie: str, *, pinned_user: str | None = None
) -> JSONResponse:
    """
    Authorize against JWT token contained in cookie
    """
    try:
        user = get_user_from_jwt(jwt_cookie, audience="auth")
        if pinned_user and user != pinned_user:
            raise ValueError("User doesn't match certificate")
        return JSONResponse(
            {"status": True}, status_code=200, headers={"Remote-User": encode_user(user)}
        )
    except ValueError as e:
        logger.error("[Cookie][%s] Denied: %s", request.client.host, str(e) or "Unspecified reason")
        return JSONResponse({"status": False}, status_code=401)


async def auth_private_token(
    request: Request, private_token: str, *, pinned_user: str | None = None
) -> JSONResponse:
    """
    Authenticate against Private-Token header
    """
    reason = None
    remote_ip = request.client.host
    user, access = get_api_access(private_token, remote_ip)
    if user and access and (not pinned_user or user == pinned_user):
        return JSONResponse(
            {"status": True},
            status_code=200,
            headers={"Remote-User": encode_user(user), "X-NOC-API-Access": access},
        )
    if not user:
        reason = "API Key not found"
    elif not access:
        reason = "API Key has no access"
    elif pinned_user and user != pinned_user:
        reason = "User doesn't match certificate"
    logger.error(
        "[Private-Token][%s|%s] Denied: %s",
        user or "NOT SET",
        remote_ip,
        reason or "Unspecified reason",
    )
    return JSONResponse({"status": False}, status_code=401)


api_key_cache = cachetools.TTLCache(100, ttl=3)


@cachetools.cached(api_key_cache)
def get_api_access(key: str, ip: str) -> tuple[str, str]:
    """
    Cached API key data

    :param key: API Key value
    :param ip: Client IP
    :return:
    """
    return APIKey.get_name_and_access_str(key, ip)


async def auth_authorization(
    request: Request, authorization: str, svc: LoginService, *, pinned_user: str | None = None
) -> JSONResponse:
    """
    Authenticate against Authorization header
    """
    if " " in authorization:
        schema, data = authorization.split(" ", 1)
        if schema == "Basic":
            return await auth_authorization_basic(
                request=request, data=data, pinned_user=pinned_user
            )
        if schema == "Bearer":
            return await auth_authorization_bearer(
                request=request, data=data, svc=svc, pinned_user=pinned_user
            )
        if schema == "Apikey":
            return await auth_private_token(
                request=request, private_token=data, pinned_user=pinned_user
            )
        logger.error(
            "[Authorization][%s] Denied: Unsupported authorization schema '%s'",
            request.client.host,
            schema,
        )
    else:
        logger.error(
            "[Authorization][%s] Denied: Unsupported authorization header",
            request.client.host,
        )
    return JSONResponse({"status": False}, status_code=401)


async def auth_authorization_basic(
    request: Request, data: str, *, pinned_user: str | None = None
) -> JSONResponse:
    """
    HTTP Basic authorization handler
    """
    remote_ip = request.client.host
    auth_data = codecs.decode(smart_bytes(data), "base64").decode()
    if ":" not in auth_data:
        logger.error("[Authorization|Basic][%s] Denied: Malformed data", remote_ip)
        return JSONResponse({"status": False}, status_code=401)
    user, password = auth_data.split(":", 1)
    credentials = {"user": user, "password": password, "ip": remote_ip}
    user = authenticate(credentials)
    if user:
        if pinned_user and user != pinned_user:
            logger.error("[Authorization|Basic][%s] user doesn't match certificate", user)
            return JSONResponse({"status": False}, status_code=401)
        register_last_login(user)
        response = JSONResponse(
            {"status": True}, status_code=200, headers={"Remote-User": encode_user(user)}
        )
        set_jwt_cookie(response, user)
        return response
    logger.error("[Authorization|Basic][%s|%s] Denied: Authentication failed", user, remote_ip)
    return JSONResponse({"status": False}, status_code=401)


async def auth_authorization_bearer(
    request: Request, data: str, svc: LoginService, pinned_user: str | None = None
) -> JSONResponse:
    """
    HTTP Bearer autorization handler
    :return:
    """
    if svc.is_revoked(data):
        return JSONResponse({"status": False}, status_code=401)
    try:
        user = get_user_from_jwt(data, audience="auth")
        if pinned_user and user != pinned_user:
            raise ValueError("User doesn't match certificate")
    except ValueError:
        logger.error(
            "[Authorization|Bearer][%s] Denied: Authentication failed", request.client.host
        )
        return JSONResponse({"status": False}, status_code=401)
    return JSONResponse(
        {"status": True}, status_code=200, headers={"Remote-User": encode_user(user)}
    )


def is_pinhole(path: str) -> bool:
    """
    Check if path should be pinholed (allowed unconditionaly)
    :return:
    """
    idx = path.find("?")
    if idx > 0:
        path = path[:idx]
    if path in PINHOLE_PATHS:
        return True
    return bool(
        path.startswith("/api/") and path.endswith("/openapi.json") and path.count("/") == 3
    )
