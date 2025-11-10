# ----------------------------------------------------------------------
# indent tokenizer tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.confdb.tokenizer.indent import IndentTokenizer


CFG1 = """# comment

interface Gi 0/1
    description testing interface
    ip address 10.0.0.1/24
    qos
        input input-map
        output output-map
#
interface Gi 0/2
    description testing interface 2
    ip address 10.0.1.1/24
    qos
        input input-map
        output output-map
"""

TOKENS1 = [
    ("interface", "Gi", "0/1"),
    ("interface", "Gi", "0/1", "description", "testing", "interface"),
    ("interface", "Gi", "0/1", "ip", "address", "10.0.0.1/24"),
    ("interface", "Gi", "0/1", "qos"),
    ("interface", "Gi", "0/1", "qos", "input", "input-map"),
    ("interface", "Gi", "0/1", "qos", "output", "output-map"),
    ("interface", "Gi", "0/2"),
    ("interface", "Gi", "0/2", "description", "testing", "interface", "2"),
    ("interface", "Gi", "0/2", "ip", "address", "10.0.1.1/24"),
    ("interface", "Gi", "0/2", "qos"),
    ("interface", "Gi", "0/2", "qos", "input", "input-map"),
    ("interface", "Gi", "0/2", "qos", "output", "output-map"),
]

CFG2 = """# Comment
interface Gi 0/1
    description testing interface
    ip address 10.0.0.1/24
    qos
        input input-map
        output output-map
        end
    end
#
interface Gi 0/2
    description testing interface 2
    ip address 10.0.1.1/24
    qos
        input input-map
        output output-map
        end
    end
"""

TOKENS2 = [
    ("interface", "Gi", "0/1"),
    ("interface", "Gi", "0/1", "description", "testing", "interface"),
    ("interface", "Gi", "0/1", "ip", "address", "10.0.0.1/24"),
    ("interface", "Gi", "0/1", "qos"),
    ("interface", "Gi", "0/1", "qos", "input", "input-map"),
    ("interface", "Gi", "0/1", "qos", "output", "output-map"),
    ("interface", "Gi", "0/2"),
    ("interface", "Gi", "0/2", "description", "testing", "interface", "2"),
    ("interface", "Gi", "0/2", "ip", "address", "10.0.1.1/24"),
    ("interface", "Gi", "0/2", "qos"),
    ("interface", "Gi", "0/2", "qos", "input", "input-map"),
    ("interface", "Gi", "0/2", "qos", "output", "output-map"),
]

CFG3 = """#
vlan 333
 description MGMT
 name MGMT
#
aaa
 authentication-scheme default
 authentication-scheme remote
  authentication-mode local radius
 authorization-scheme default
 accounting-scheme default
 domain default
 domain default_admin
  authentication-scheme remote
  radius-server aaa_server
 local-user root password irreversible-cipher %^%#XXXXXXX%#
 local-user root privilege level 15
 local-user root ftp-directory flash:
 local-user root service-type telnet terminal ssh ftp
#
ntp-service server disable"""

TOKENS3 = [
    ("vlan", "333"),
    ("vlan", "333", "description", "MGMT"),
    ("vlan", "333", "name", "MGMT"),
    ("aaa",),
    ("aaa", "authentication-scheme", "default"),
    ("aaa", "authentication-scheme", "remote"),
    ("aaa", "authentication-scheme", "remote", "authentication-mode", "local", "radius"),
    ("aaa", "authorization-scheme", "default"),
    ("aaa", "accounting-scheme", "default"),
    ("aaa", "domain", "default"),
    ("aaa", "domain", "default_admin"),
    ("aaa", "domain", "default_admin", "authentication-scheme", "remote"),
    ("aaa", "domain", "default_admin", "radius-server", "aaa_server"),
    ("aaa", "local-user", "root", "password", "irreversible-cipher", "%^%#XXXXXXX%#"),
    ("aaa", "local-user", "root", "privilege", "level", "15"),
    ("aaa", "local-user", "root", "ftp-directory", "flash:"),
    ("aaa", "local-user", "root", "service-type", "telnet", "terminal", "ssh", "ftp"),
    ("ntp-service", "server", "disable"),
]

CFG4 = """! Test config
#
  http server
#
interface Fa 0/1
  description 1
#
interface Fa 0/2
  description 2
#
#
router ospf
"""

TOKENS4 = [
    ("http", "server"),
    ("interface", "Fa", "0/1"),
    ("interface", "Fa", "0/1", "description", "1"),
    ("interface", "Fa", "0/2"),
    ("interface", "Fa", "0/2", "description", "2"),
    ("router", "ospf"),
]


@pytest.mark.parametrize(
    ("input", "config", "expected"),
    [
        (CFG1, {"line_comment": "#"}, TOKENS1),
        (CFG2, {"line_comment": "#", "end_of_context": "end"}, TOKENS2),
        (CFG3, {"line_comment": "#"}, TOKENS3),
        (CFG4, {"line_comment": "!", "end_of_context": "#"}, TOKENS4),
    ],
)
def test_tokenizer(input, config, expected):
    tokenizer = IndentTokenizer(input, **config)
    assert list(tokenizer) == expected
