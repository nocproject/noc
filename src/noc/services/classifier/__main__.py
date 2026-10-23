# ----------------------------------------------------------------------
# Classifier service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.services.classifier.service import ClassifierService


if __name__ == "__main__":
    ClassifierService().start()
