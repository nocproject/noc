# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Extreme
# OS:     XOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import numpy as np
from itertools import izip_longest
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Extreme.XOS"
    pattern_prompt = r"^(\*\s)?(Slot-\d+ )?\S+? #"
    pattern_syntax_error = \
        r"%% (Incomplete command|Invalid input detected at)"
    command_disable_pager = "disable clipaging"
    pattern_more = [
        (r"^Press <SPACE> to continue or <Q> to quit:", " "),
        (r"^Do you want to continue with download and remove existing files from internal-memory\? \(y/N\)", "y\n"),
        (r"Do you want to install image after downloading\? \(y - yes, n - no, \<cr\> - cancel\)", "y\n"),
        (r"Are you sure you want to reboot the stack\? \(y/N\)", "y\n"),
        (r"Do you want to save configuration changes to currently selected configuration file (primary.cfg) and reboot?"
         r"(y - save and reboot, n - reboot without save, <cr> - cancel command)", "y\n"),
        (r"Do you want to save configuration to \S+ and overwrite it\? \(y/N\)", "y\n")
    ]

    def get_interface_names(self, name):
        """
        for stack ports in non stack device 1:49
        """
        names = []
        if ":" in name:
            names += [name.split(":")[-1]]
        return names

    @staticmethod
    def update_dict(s, d):
        for k in d:
            if k in s:
                s[k] += d[k]
            else:
                s[k] = d[k]

    @staticmethod
    def parse_header(v):
        """
        Parse header structured multiline format:
        Config    Current Agg     Min    Ld Share  Flags Ld Share  Agg Link  Link Up
        Master    Master  Control Active Algorithm       Group     Mbr State Transitions
        :param v:
        :return: Dictionary {start column position: header}
        {10: 'Config Master', 18: 'Current Master', 26: 'Agg Control', 33: 'Min Active',
         43: 'Ld Share Algorithm', 49: 'Flags ', 59: 'Ld Share Group', 63: 'Agg Mbr', 69: 'Link State'}
        """
        head = []
        empty_header = None
        header = {}

        for num, lines in enumerate(izip_longest(*v, fillvalue='-')):
            #
            if empty_header is None:
                empty_header = (' ',) * len(lines)
                head += [lines]
                continue
            if set(head[-1]) == {' '} and lines != empty_header:
                head = np.array(head)
                # Transpone list header string
                header[num] = " ".join(["".join(s).strip() for s in head.transpose().tolist()])
                head = []
            head += [lines]
        else:
            # last column
            head = np.array(head)
            header[num] = " ".join(["".join(s).strip(" -") for s in head.transpose().tolist()])
        return header

    def parse_table_struct(self, v, header_start="", header_end="",
                           table_start="=======", table_end="======="):
        """
        Parse table with structured table format:
        ex:
        Config    Current Agg     Min    Ld Share  Flags Ld Share  Agg Link  Link Up
        Master    Master  Control Active Algorithm       Group     Mbr State Transitions
        ================================================================================
          1:47            LACP       1    L3_L4     A     1:47      -     R       0
                                          L3_L4           1:48      -     R       0
          1:49   1:49     LACP       1    L3_L4     A     1:49      Y     A       2
                                          L3_L4           2:49      Y     A       3
        ================================================================================
          parse_table_struct(t, header_start="Config", table_start="=======", table_end="=======")
        or

        Lag        Actor    Actor   Partner            Partner  Partner  Agg
                   Sys-Pri  Key     MAC                Sys-Pri  Key      Count
        --------------------------------------------------------------------------------
        1:47           0    0x0417  00:00:00:00:00:00      0    0x0000   0
        1:49           0    0x0419  02:04:96:98:d1:86      0    0x03ff   2
        ================================================================================
        parse_table_struct(t, header_start="Lag", table_start="-------", table_end="=======")
        :param v:
        :param header_start:
        :param header_end:
        :param table_start:
        :param table_end:
        :return:
        """
        r = []
        header = []
        is_header = False
        is_body = False
        ph = {}
        for line in v.splitlines():
            if table_end in line and is_body:
                is_body = False
                continue

            if not is_body:
                # Check start table body (end table header)
                if table_start in line:
                    is_header = False
                    is_body = True
                    if header:
                        ph = self.parse_header(header)
                        header = []
            elif is_body:
                i = 0
                field = {}
                for num in sorted(ph):
                    left = i - 1 if i else i
                    right = num - 1
                    v = line[left:right].strip()
                    field[ph[num]] = [v] if v else []
                    i = num
                if not field[ph[min(ph)]] and r:
                    self.update_dict(r[-1], field)
                else:
                    r += [field]
                pass

            if not is_header and not is_body:
                # Check start header lines
                if header_start in line:
                    is_header = True
                    is_body = False
            if is_header:
                header += [line]

        return r
