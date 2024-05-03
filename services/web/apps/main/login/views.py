# ---------------------------------------------------------------------
# main.login application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.config import config
from noc.services.web.base.extapplication import ExtApplication, view
from noc.core.version import version


class LoginApplication(ExtApplication):
    """
    main.login application
    """

    @view(method=["GET"], url="^$", url_name="desktop", access=True)
    def view_login(self, request):
        """
        Render application root template
        """
        # Prepare settings
        favicon_url = config.customization.favicon_url
        if favicon_url.endswith(".png"):
            favicon_mime = "image/png"
        elif favicon_url.endswith(".jpg") or favicon_url.endswith(".jpeg"):
            favicon_mime = "image/jpeg"
        else:
            favicon_mime = None
        setup = {
            "installation_name": config.installation_name,
            "theme": config.web.theme,
            "logo_url": config.customization.logo_url,
            "logo_width": config.customization.logo_width,
            "logo_height": config.customization.logo_height,
            "brand": version.brand,
            "branding_color": config.customization.branding_color,
            "branding_background_color": config.customization.branding_background_color,
            "favicon_url": favicon_url,
            "favicon_mime": favicon_mime,
            "language": config.language,
        }
        return self.render(request, "login.html", setup=setup)
