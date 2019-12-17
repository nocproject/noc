# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc.core.text legacy wrappers
# flake8: noqa
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import warnings

# NOC modules
from noc.core.text import (
    parse_table,
    strip_html_tags,
    xml_to_table,
    list_to_ranges,
    ranges_to_list,
    replace_re_group,
    indent,
    split_alnum,
    find_indented,
    parse_kv,
    str_dict,
    quote_safe_path,
    to_seconds,
    format_table,
    clean_number,
    safe_shadow,
    ch_escape,
    tsv_escape,
    parse_table_header,
)
from noc.core.deprecations import RemovedInNOC2001Warning

warnings.warn(
    "noc.lib.text is deprecated and will be removed in NOC 20.1. "
    "Please replace imports to noc.core.text",
    RemovedInNOC2001Warning,
    stacklevel=2,
)
