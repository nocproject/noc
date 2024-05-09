# ----------------------------------------------------------------------
# Translation utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import logging
import gettext

# NOC modules
from noc.core.comp import smart_text

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
            with open(mo_path, mode="rb") as f:
                _ugettext = gettext.GNUTranslations(f).gettext
        else:
            logger.info("No translation for language '%s'. Using 'en' instead", lang)


def _ugettext(x):
    return x


def ugettext(x):
    return smart_text(_ugettext(x))
