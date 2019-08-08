# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Iskratel
# OS:     MBAN
# Compatible:
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Iskratel.MBAN"
    # Iskratel do not have "enable_super" command
    # pattern_unprivileged_prompt = r"^\S+?>"
    pattern_username = r"^user id :"
    pattern_prompt = r"^\S+?>"
    pattern_more = [
        (r"^Press any key to continue or Esc to stop scrolling.\r\n", " "),
        (r"^Press any key to continue", " "),  # Need more examples
    ]
    # pattern_more = "^Press any key to continue or Esc to stop scrolling.\r\n"
    pattern_syntax_error = r"Illegal command name"
    command_more = " "
    command_exit = "exit"
    command_save_config = "save"
    config_volatile = ["^%.*?$"]
    enable_cli_session = False
    command_submit = "\r\n"
    rogue_chars = ["\r\x00"]

    rx_iface_match = re.compile(r"^(\w+?)(\d+)$")

    def convert_interface_name(self, s, board=0):
        if board and self.rx_iface_match.match(s):
            # appen boarn number to ifName
            return "%s%s/%s" % (
                self.rx_iface_match.match(s).group(1),
                board if board else "",
                self.rx_iface_match.match(s).group(2),
            )
        if s.startswith("ISKRATEL:"):
            # for SNMP ifDescr (ISKRATEL: atm 5/1, ISKRATEL: ethernet 5/1)
            _, s = s.split(":")
            s = s.strip()
            if s.startswith("ethernet"):
                s = "fasteth" + s.split("/")[-1]
            elif s.startswith("atm"):
                s = "dsl" + s.split("/")[-1]
        elif s.startswith("port"):
            # SNMP ifName (port1, port2)
            s = "dsl" + self.rx_iface_match.match(s).group(2)
        elif s.startswith("internal MN port"):
            s = "mng0"
        return s

    rx_board = re.compile(
        r"(?P<brd_num>\d+)\s*"
        r"(?P<brd_type>\S+)\s*"
        r"(?P<brd_req_lables>\S+)\s*"
        r"(?P<brd_act_label>\S+)\s*"
        r"(?P<brd_ser_num>\S+)\s*"
        r"(?P<brd_oper_status>.+)"
    )

    def get_board(self, script):
        """
        Brd Cmp  Type        Req.Label   Act.Label     Ser.number      Oper.State
        --------------------------------------------------------------- -----------------
        6     ADSL2+(SGN)   UTA6044AD   UTA6044AD09N  Z08092012G      In Service
        --------------------------------------------------------------------------------

        :param script:
        :return:
        """
        c = self.rx_board.findall(script.cli("show board", cached=True))
        if c:
            return c[0]
        else:
            script.logger.warning("Board is not match")
            return 0, "", "", "", "", ""
