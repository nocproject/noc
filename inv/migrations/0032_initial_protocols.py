# ----------------------------------------------------------------------
# Create initial protocols for migration purposes
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from uuid import UUID

# Third-party modules
import bson
from bson.int64 import Int64
from bson.binary import Binary
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Insert Technologies
        bulk = [
            UpdateOne(
                {"_id": bson.ObjectId("6532734d6aad5b611082bf55")},
                {
                    "$set": {
                        "name": "Energetics",
                        "uuid": UUID("80a9c79c-3f43-4718-8d60-55815090cdc3"),
                        "single_service": False,
                        "single_client": False,
                        "allow_children": False,
                        "bi_id": Int64(5829566886584370399),
                    }
                },
                upsert=True,
            ),
            UpdateOne(
                {"_id": bson.ObjectId("65327510bf6b74584155a94f")},
                {
                    "$set": {
                        "name": "USB",
                        "uuid": UUID("05aa3539-fed0-4253-b2fa-c6670264f1b8"),
                        "single_service": False,
                        "single_client": False,
                        "allow_children": False,
                        "bi_id": Int64(789474188471280328),
                    }
                },
                upsert=True,
            ),
            UpdateOne(
                {"_id": bson.ObjectId("653277006aad5b611082bf5c")},
                {
                    "$set": {
                        "name": "Ethernet",
                        "uuid": UUID("533cdc92-b6f7-4769-9ffd-253693aa28b2"),
                        "single_service": False,
                        "single_client": False,
                        "allow_children": False,
                        "bi_id": Int64(8517014800812630690),
                    }
                },
                upsert=True,
            ),
            UpdateOne(
                {"_id": bson.ObjectId("65327760bf6b74584155a953")},
                {
                    "$set": {
                        "name": "XPON",
                        "uuid": UUID("2904804b-8bd8-4de8-b727-2deacf48c5a9"),
                        "description": "A passive optical network (PON) is a fiber-optic telecommunications technology for delivering broadband network access to end-customers",
                        "single_service": False,
                        "single_client": False,
                        "allow_children": False,
                        "bi_id": Int64(9177230454852081095),
                    }
                },
                upsert=True,
            ),
            UpdateOne(
                {"_id": bson.ObjectId("653277c66aad5b611082bf5e")},
                {
                    "$set": {
                        "name": "Trasceiver",
                        "uuid": UUID("aef9bb4a-4ff1-4c6e-b7d7-cd7309b8debd"),
                        "single_service": False,
                        "single_client": False,
                        "allow_children": False,
                        "bi_id": Int64(2211136824221559425),
                    }
                },
                upsert=True,
            ),
            UpdateOne(
                {"_id": bson.ObjectId("65327d056aad5b611082bf6e")},
                {
                    "$set": {
                        "name": "Serial",
                        "uuid": UUID("1b36e203-e78a-4389-bbc9-ad1c59d034ac"),
                        "single_service": False,
                        "single_client": False,
                        "allow_children": False,
                        "bi_id": Int64(6974045341783340635),
                    }
                },
                upsert=True,
            ),
            UpdateOne(
                {"_id": bson.ObjectId("65335aeac0fe77cd7156a8eb")},
                {
                    "$set": {
                        "name": "WDM",
                        "uuid": UUID("10338c90-ba17-4cba-bcfb-6d4884d743fe"),
                        "description": "In fiber-optic communications, wavelength-division multiplexing (WDM) is a technology which multiplexes a number of optical carrier signals onto a single optical fiber by using different wavelengths (i.e., colors) of laser light.[1] ",
                        "single_service": False,
                        "single_client": False,
                        "allow_children": False,
                        "bi_id": Int64(4386911184028583206),
                    }
                },
                upsert=True,
            ),
            UpdateOne(
                {"_id": bson.ObjectId("65336f2d8989dc8dd4489148")},
                {
                    "$set": {
                        "name": "Modulator-Demodulator",
                        "uuid": UUID("f405cc3d-cbe8-4e43-8c58-2bd7266fb8d5"),
                        "description": "A modulator-demodulator or modem is a computer hardware device that converts data from a digital format into a format suitable for an analog transmission medium such as telephone or radio",
                        "single_service": False,
                        "single_client": False,
                        "allow_children": False,
                        "bi_id": Int64(8030802649834209715),
                    }
                },
                upsert=True,
            ),
            UpdateOne(
                {"_id": bson.ObjectId("653375108989dc8dd448914c")},
                {
                    "$set": {
                        "name": "XDSL",
                        "uuid": UUID("d2aac109-6506-4014-9a98-15537ec4c41f"),
                        "description": "Digital subscriber line (DSL; originally digital subscriber loop) is a family of technologies that are used to transmit digital data over telephone lines. In telecommunications marketing, the term DSL is widely understood to mean asymmetric digital subscriber line (ADSL), the most commonly installed DSL technology, for Internet access.",
                        "single_service": False,
                        "single_client": False,
                        "allow_children": False,
                        "bi_id": Int64(270365769819082249),
                    }
                },
                upsert=True,
            ),
            UpdateOne(
                {"_id": bson.ObjectId("653376058989dc8dd4489152")},
                {
                    "$set": {
                        "name": "PSTN",
                        "uuid": UUID("8e987de1-e2a0-4393-9d98-37b0f5cb55f1"),
                        "description": "The public switched telephone network (PSTN) is the aggregate of the world's telephone networks that are operated by national, regional, or local telephony operators.",
                        "single_service": False,
                        "single_client": False,
                        "allow_children": False,
                        "bi_id": Int64(6193662985572453528),
                    }
                },
                upsert=True,
            ),
            UpdateOne(
                {"_id": bson.ObjectId("6533a1268989dc8dd4489158")},
                {
                    "$set": {
                        "name": "Cisco | Interface Card",
                        "uuid": UUID("29426285-f1e7-4251-ad5f-a32cbc35709a"),
                        "description": "Technology connect interface card (IC) to integrated router.",
                        "single_service": False,
                        "single_client": False,
                        "allow_children": False,
                        "bi_id": Int64(5369425707749880806),
                    }
                },
                upsert=True,
            ),
            UpdateOne(
                {"_id": bson.ObjectId("6533b6aee74019b4dc11adbf")},
                {
                    "$set": {
                        "name": "IEEE 802.11",
                        "uuid": UUID("bd76f5ae-cc89-47ee-8b42-b8d8e89eefe3"),
                        "description": "IEEE 802.11 is part of the IEEE 802 set of local area network (LAN) technical standards, and specifies the set of media access control (MAC) and physical layer (PHY) protocols for implementing wireless local area network (WLAN) computer communication.",
                        "single_service": False,
                        "single_client": False,
                        "allow_children": False,
                        "bi_id": Int64(9135212433141383564),
                    }
                },
                upsert=True,
            ),
        ]
        self.mongo_db.technologies.bulk_write(bulk)
        # Protocols
        bulk = [
            {
                "_id": bson.ObjectId("65318b63e1d347d78ade75a0"),
                "name": "RS 485",
                "code": "RS485",
                "uuid": UUID("1dc4e929-f4ec-481f-b2e9-f0c9eb103dd3"),
                "technology": bson.ObjectId("65327d056aad5b611082bf6e"),
                "connection_schema": "BD",
                "discriminators": [
                    {
                        "code": "A",
                        "data": [{"interface": "signal_level", "attr": "logic_0", "value": 1}],
                    },
                    {
                        "code": "B",
                        "data": [{"interface": "signal_level", "attr": "logic_0", "value": 0}],
                    },
                ],
                "bi_id": Int64("2691023279856402135"),
                "description": "RS485",
                "discriminator_source": "protocol",
            },
            {
                "_id": bson.ObjectId("653273dfbf6b74584155a945"),
                "name": "220 VAC",
                "code": "220VAC",
                "description": "220VAC",
                "uuid": UUID("177b3bcc-f07d-4d03-85fe-3a257ef2f74e"),
                "technology": bson.ObjectId("6532734d6aad5b611082bf55"),
                "data": [],
                "connection_schema": "U",
                "discriminators": [],
                "bi_id": Int64("3843442863367160807"),
            },
            {
                "_id": bson.ObjectId("65327451bf6b74584155a947"),
                "name": "110 VAC",
                "code": "110VAC",
                "description": "110 VAC",
                "uuid": UUID("f6f8744c-f90d-42f9-b7b1-d1bcf4ccdd04"),
                "technology": bson.ObjectId("6532734d6aad5b611082bf55"),
                "data": [],
                "connection_schema": "U",
                "discriminators": [],
                "bi_id": Int64("7471660321289693384"),
            },
            {
                "_id": bson.ObjectId("6532745ebf6b74584155a949"),
                "name": "-48 VDC",
                "code": "-48VDC",
                "description": "-48 VDC",
                "uuid": UUID("50c68d89-1f54-47e0-ad60-b3569c3a0f89"),
                "technology": bson.ObjectId("6532734d6aad5b611082bf55"),
                "data": [],
                "connection_schema": "U",
                "discriminators": [],
                "bi_id": Int64("5236313237307741531"),
            },
            {
                "_id": bson.ObjectId("65327481bf6b74584155a94b"),
                "name": "+24 VDC",
                "code": "+24VDC",
                "description": "+24 VDC",
                "uuid": UUID("3ade4e37-1804-4d10-9db2-7560e8df1390"),
                "technology": bson.ObjectId("6532734d6aad5b611082bf55"),
                "data": [],
                "connection_schema": "U",
                "discriminators": [],
                "bi_id": Int64("7978576983590619171"),
            },
            {
                "_id": bson.ObjectId("653274b8bf6b74584155a94d"),
                "name": "POE",
                "code": "POE",
                "description": "Power Over Ethernet",
                "uuid": UUID("8e561346-ff0a-4867-9722-4f2033d78f94"),
                "technology": bson.ObjectId("6532734d6aad5b611082bf55"),
                "data": [],
                "connection_schema": "U",
                "discriminators": [],
                "bi_id": Int64("5863407299445089500"),
            },
            {
                "_id": bson.ObjectId("653275736aad5b611082bf58"),
                "name": "USB 1.1",
                "code": "USB11",
                "description": "USB 1.1",
                "uuid": UUID("97f79254-7fd7-40dc-8371-ead35bf9df1f"),
                "technology": bson.ObjectId("65327510bf6b74584155a94f"),
                "data": [],
                "connection_schema": "BO",
                "discriminators": [],
                "bi_id": Int64("2386839526466703340"),
            },
            {
                "_id": bson.ObjectId("6532758b6aad5b611082bf5a"),
                "name": "USB 1.0",
                "code": "USB10",
                "description": "USB 1.0",
                "uuid": UUID("9a5b71d7-f2d6-4c50-97c5-6c820dc2774a"),
                "technology": bson.ObjectId("65327510bf6b74584155a94f"),
                "data": [],
                "connection_schema": "BO",
                "discriminators": [],
                "bi_id": Int64("6887644278386016264"),
            },
            {
                "_id": bson.ObjectId("653279056aad5b611082bf60"),
                "name": "TransEth100M",
                "code": "TransEth100M",
                "description": "Interface for device transievers module",
                "uuid": UUID("e21731cb-de01-4ad4-9eea-894662450149"),
                "technology": bson.ObjectId("653277c66aad5b611082bf5e"),
                "data": [],
                "connection_schema": "BO",
                "discriminators": [],
                "bi_id": Int64("4903870090979666752"),
            },
            {
                "_id": bson.ObjectId("653279736aad5b611082bf62"),
                "name": "TransEth1G",
                "code": "TransEth1G",
                "description": "Interface for device transivers module",
                "uuid": UUID("68c8d26b-6ab8-4fa1-b567-0c8abda96dcc"),
                "technology": bson.ObjectId("653277c66aad5b611082bf5e"),
                "data": [],
                "connection_schema": "BO",
                "discriminators": [],
                "bi_id": Int64("1832286335929498848"),
            },
            {
                "_id": bson.ObjectId("6532797e6aad5b611082bf64"),
                "name": "TransEth10G",
                "code": "TransEth10G",
                "description": "Interface for device transievers module",
                "uuid": UUID("01153625-15c4-4aa5-9989-dfb862c474ed"),
                "technology": bson.ObjectId("653277c66aad5b611082bf5e"),
                "data": [],
                "connection_schema": "BO",
                "discriminators": [],
                "bi_id": Int64("275389514543160960"),
            },
            {
                "_id": bson.ObjectId("653279866aad5b611082bf66"),
                "name": "TransEth40G",
                "code": "TransEth40G",
                "description": "Interface for device transievers module",
                "uuid": UUID("0246c61e-1247-4a12-91e5-efab706a8c37"),
                "technology": bson.ObjectId("653277c66aad5b611082bf5e"),
                "data": [],
                "connection_schema": "BO",
                "discriminators": [],
                "bi_id": Int64("6932632725653533124"),
            },
            {
                "_id": bson.ObjectId("653279906aad5b611082bf68"),
                "name": "TransEth100G",
                "code": "TransEth100G",
                "description": "Interface for device transievers module",
                "uuid": UUID("326711d5-fbe8-4131-8b05-d7e7e718ab97"),
                "technology": bson.ObjectId("653277c66aad5b611082bf5e"),
                "data": [],
                "connection_schema": "BO",
                "discriminators": [],
                "bi_id": Int64("5286875465422562855"),
            },
            {
                "_id": bson.ObjectId("653279a76aad5b611082bf6a"),
                "name": "TransSTM1",
                "code": "TransSTM1",
                "description": "Interface for device transievers module",
                "uuid": UUID("4229fadc-55e0-4fd4-9f72-a87155350f01"),
                "technology": bson.ObjectId("653277c66aad5b611082bf5e"),
                "data": [],
                "connection_schema": "BO",
                "discriminators": [],
                "bi_id": Int64("556182039934468284"),
            },
            {
                "_id": bson.ObjectId("65327a226aad5b611082bf6c"),
                "name": "GPON",
                "code": "GPON",
                "uuid": UUID("7fb161b9-f697-45eb-ba98-d6af4b841fcd"),
                "technology": bson.ObjectId("65327760bf6b74584155a953"),
                "data": [],
                "connection_schema": "BD",
                "discriminators": [],
                "bi_id": Int64("1659033913694307604"),
            },
            {
                "_id": bson.ObjectId("65327d2cbf6b74584155a955"),
                "name": "RS-232",
                "code": "RS232",
                "description": "RS 232",
                "uuid": UUID("5e156067-efc3-4b82-a57e-bd2d6cdfd2a9"),
                "technology": bson.ObjectId("65327d056aad5b611082bf6e"),
                "data": [],
                "connection_schema": "BD",
                "discriminators": [],
                "bi_id": Int64("5205790489830554522"),
            },
            {
                "_id": bson.ObjectId("65328f136aad5b611082bf71"),
                "name": "10BASE-T",
                "code": "10BASET",
                "uuid": UUID("f93f1161-acc0-4f8e-b574-5cca89d76fec"),
                "technology": bson.ObjectId("653277006aad5b611082bf5c"),
                "data": [],
                "connection_schema": "BO",
                "discriminators": [],
                "bi_id": Int64("8875579118616285837"),
                "description": "10BASE-T, 10Mbit/s",
            },
            {
                "_id": bson.ObjectId("65328f2d6aad5b611082bf73"),
                "name": "100BASE-TX",
                "code": "100BASETX",
                "description": "100BASE-TX, 100Mbit/s",
                "uuid": UUID("6699197d-7086-40b2-a6aa-7e6c6956e227"),
                "technology": bson.ObjectId("653277006aad5b611082bf5c"),
                "data": [],
                "connection_schema": "BO",
                "discriminators": [],
                "bi_id": Int64("2565077446723564560"),
            },
            {
                "_id": bson.ObjectId("65328f4e6aad5b611082bf75"),
                "name": "1000BASE-T",
                "code": "1000BASET",
                "description": "1000BASE-T, 1Gbit/s 1000BASE-T (also known as IEEE 802.3ab) is a standard for Gigabit Ethernet over copper wiring.",
                "uuid": UUID("65d9549b-ea6f-4043-9bc5-d99f06814be4"),
                "technology": bson.ObjectId("653277006aad5b611082bf5c"),
                "data": [],
                "connection_schema": "BO",
                "discriminators": [],
                "bi_id": Int64("2937120087927440470"),
            },
            {
                "_id": bson.ObjectId("65328f6d6aad5b611082bf77"),
                "name": "1000BASE-TX",
                "code": "1000BASETX",
                "description": "1000BASE-TX, 1Gbit/s. This standard has never been implemented on commercially available equipment; do not use it.",
                "uuid": UUID("04a1dff7-0b12-4df0-a1de-f353626ebc84"),
                "technology": bson.ObjectId("653277006aad5b611082bf5c"),
                "data": [],
                "connection_schema": "BO",
                "discriminators": [],
                "bi_id": Int64("2727256255452469071"),
            },
        ]
