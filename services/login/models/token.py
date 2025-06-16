# ----------------------------------------------------------------------
# TokenResponse
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Union, Literal

# Third-party modules
from pydantic import BaseModel


class ROPCGrantRequest(BaseModel):
    """
    RFC-6749 Resource Owner Password Credentials Grant.
    Section 4.3
    """

    grant_type: Literal["password"]
    username: str
    password: str
    scope: Optional[str] = None


class CCGrantRequest(BaseModel):
    """
    RFC-6749 Client Credentials Grant
    Section 4.4
    """

    grant_type: Literal["client_credentials"]
    scope: Optional[str] = None


class RefreshRequest(BaseModel):
    """
    RFC-6749 Refreshing an Access Token
    Section: 6
    """

    grant_type: Literal["refresh_token"]
    refresh_token: str
    scope: Optional[str] = None


TokenRequest = Union[RefreshRequest, ROPCGrantRequest, CCGrantRequest]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
