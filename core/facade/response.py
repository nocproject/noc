# ---------------------------------------------------------------------
# SVG Response
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.http import HttpResponse

# NOC modules
from noc.core.svg import SVG


def svg_response(svg: SVG) -> HttpResponse:
    """
    Get HttpResponse for SVG.

    Args:
        svg: SVG to stream.

    Returns:
        Wrapped SVG response.
    """
    return HttpResponse(
        svg.to_string(),
        content_type="image/svg+xml",
        status=200,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )
