# ----------------------------------------------------------------------
# /api/login/token handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from http import HTTPStatus
from typing import Optional, Dict
import codecs

# Third-party modules
from fastapi import APIRouter, Request, Header, Depends
from starlette.responses import JSONResponse
from pydantic import ValidationError, TypeAdapter

# NOC modules
from noc.config import config
from noc.aaa.models.user import User
from noc.core.comp import smart_text, smart_bytes
from noc.core.service.deps.service import get_service
from ..models.token import TokenRequest, TokenResponse
from ..auth import authenticate, get_jwt_token, get_user_from_jwt
from ..service import LoginService

router = APIRouter()
ta_TokenRequest = TypeAdapter(TokenRequest)


@router.post("/api/login/token", response_model=TokenResponse, tags=["login"])
async def token(
    request: Request,
    # @todo: Find the way to pass req to openapi schema
    # req: TokenRequest,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    svc: LoginService = Depends(get_service),
):
    # NB: Some testing tools are dumb enough to support only application/x-www-form-urlencoded
    # kind of request. So we need this kind of
    # MADNESS BELOW -->
    content_type = request.headers.get("Content-Type")
    try:
        # Content-Type := type "/" subtype *[";" parameter]
        content_type = content_type.split(";")[0]
        if content_type in ("application/json", "text/json"):
            req = ta_TokenRequest.validate_python(await request.json())
        elif content_type == "application/x-www-form-urlencoded":
            req = ta_TokenRequest.validate_python(await request.form())
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_request",
                    "error_description": [
                        {
                            "loc": ["__root__", "content_type"],
                            "msg": f"Invalid content type {content_type}",
                        }
                    ],
                },
            )
    except ValidationError as e:
        return await svc.request_validation_error_handler(request, e)
    # <-- MADNESS ABOVE
    auth_req: Optional[Dict[str, str]]
    if req.grant_type == "refresh_token":
        # Refresh token
        if svc.is_revoked(req.refresh_token):
            return JSONResponse(
                content={"error": "invalid_grant", "error_description": "Token is expired"},
                status_code=HTTPStatus.FORBIDDEN,
            )
        try:
            user = get_user_from_jwt(req.refresh_token, audience="refresh")
        except ValueError as e:
            return JSONResponse(
                content={
                    "error": "unauthorized_client",
                    "error_description": "Access denied (%s)" % e,
                },
                status_code=HTTPStatus.FORBIDDEN,
            )
        await svc.revoke_token(req.refresh_token, "refresh")
        return get_token_response(user)
    elif req.grant_type == "password":
        # ROPCGrantRequest
        auth_req = {"user": req.username, "password": req.password, "ip": request.client.host}
    elif req.grant_type == "client_credentials" and authorization:
        # CCGrantRequest + Basic auth header
        schema, data = authorization.split(" ", 1)
        if schema != "Basic":
            return JSONResponse(
                content={
                    "error": "unsupported_grant_type",
                    "error_description": "Basic authorization header required",
                },
                status_code=HTTPStatus.BAD_REQUEST,
            )
        auth_data = smart_text(codecs.decode(smart_bytes(data), "base64"))
        if ":" not in auth_data:
            return JSONResponse(
                content={
                    "error": "invalid_request",
                    "error_description": "Invalid basic auth header",
                },
                status_code=HTTPStatus.BAD_REQUEST,
            )
        user, password = auth_data.split(":", 1)
        auth_req = {"user": user, "password": password, "ip": request.client.host}
    else:
        return JSONResponse(
            content={"error": "unsupported_grant_type", "error_description": "Invalid grant type"},
            status_code=HTTPStatus.BAD_REQUEST,
        )
    # Authenticate
    if auth_req:
        user = authenticate(auth_req)
        if user:
            # Register last login
            if config.login.register_last_login:
                u = User.get_by_username(user)
                if u:
                    u.register_login()
            return get_token_response(user)
    return JSONResponse(
        content={
            "error": "invalid_client",
            "error_description": "Username or password is incorrect",
        },
        status_code=HTTPStatus.UNAUTHORIZED,
    )


def get_token_response(user: str) -> TokenResponse:
    expire = config.login.session_ttl
    return TokenResponse(
        access_token=get_jwt_token(user, expire=expire, audience="auth"),
        token_type="bearer",
        expires_in=expire,
        refresh_token=get_jwt_token(user, expire=expire, audience="refresh"),
    )
