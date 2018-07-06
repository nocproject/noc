# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dev.Quiz tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.dev.models.quiz import Quiz


class TestDevQuiz(BaseDocumentTest):
    model = Quiz
