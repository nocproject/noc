# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Translation utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

import gettext
import logging
## Python modules
import os

logger = logging.getLogger(__name__)


def set_translation(service, lang):
    """
    Set current translation to lang
    """
    global _ugettext

    if lang != "en":
        # Check .mo file
        mo_path = "services/%s/translations/%s/LC_MESSAGES/messages.mo" % (service, lang)
        if os.path.exists(mo_path):
            logger.info("Setting '%s' translation", mo_path)
            with open(mo_path) as f:
                _ugettext = gettext.GNUTranslations(f).ugettext
        else:
            logger.info(
                "No translation for language '%s'. Using 'en' instead",
                lang
            )


_ugettext = lambda x: x
ugettext = lambda x: _ugettext(x)
