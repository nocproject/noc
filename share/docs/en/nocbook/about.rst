.. _about:

About NOC
=========

NOC is an Operation Support System (OSS) for the Network's Operation Centers (NOC). Primary users of NOC are the
telecommunication companies, service provides and enterprise networks.
NOC primary goal is to be a glue getting various operation processes together.

Areas covered by NOC include:

    - Multi-VRF address space management: Full control over VRF, IPv4 block and address allocation and usage.
    - Virtual circuits management: VLANs can be created and destroyed directly from NOC. All changes propagate to network equipment using defined policies.
    - Service activation and provisioning: Interaction with network equipment to automate routine tasks like inventory, port activation, etc.
    - Configuration management: Control over current configuration and changes of network equipment configs, DNS zones, prefix lists and RPSL objects
    - DNS provisioning: DNS zone management, generation and provisioning to DNS servers according to defined policy
    - Peering management: BGP peer inventory, various RPSL objects generation and provisioning to RIR's databases
    - Fault management: Collect and process syslog messages and SNMP traps from equipment, maintain lifecycle of event, reduce amount of seen events to thouse which really need attention
    - Performance management: Collect and process various performance data to analyze network trends.
    - Knowledge base: wiki-like knowledge base to share the knowledge, store documentation, scans and charts.
    
NOC is Open Source Software distributed under the terms of BSD-like :ref:`LICENSE`.

Key Features
------------


A Brief History
---------------
NOC starts its way in Effortel Russia in late 2007 as telephone number and IP address space database and was quickly recognized
as a single information storage. DNS provisioning appears shortly after. After an year of internal usage NOC was released as
an open source project. Then `Badoo Development <http://badoo.com/>`_ and `Innova Group <http://inn.ru/>`_ adopts NOC and
the project became to gain momentum.
