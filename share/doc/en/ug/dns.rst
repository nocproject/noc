***
DNS
***
Overview
========
DNS Provisioning. Generates forward and reverse zones for allocated IP addresses (ip module). Contains web-interface
for DNS Zone editing and provisioning. Generated DNS Zones are stored in cm repo.
Resulting zones and configuration are provisioning to DNS Servers.
Zones can be redistributed via several authoritative DNS servers (may be of different types) allowing to share load.

Terminology
============
* Zone
* Reverse Zone
* Generatior
* Nameserver

Forms
=====
Zones
-----
Permissions
^^^^^^^^^^^
======= ========================================
add     dns | DNS Zone | Can add DNS Zone
change  dns | DNS Zone | Can change DNS Zone
delete  dns | DNS Zone | Can delete DNS Zone
======= ========================================

Setup
=====
DNS Servers
-----------
Permissions
^^^^^^^^^^^
======= ========================================
add     dns | DNS Server | Can add DNS Server
change  dns | DNS Server | Can change DNS Server
delete  dns | DNS Server | Can delete DNS Server
======= ========================================

Zone Profiles
-------------
Permissions
^^^^^^^^^^^
======= ========================================
add     dns | dns zone profile | Can add dns zone profile
change  dns | dns zone profile | Can change dns zone profile
delete  dns | dns zone profile | Can delete dns zone profile
======= ========================================

Zone Record Types
-----------------
Permissions
^^^^^^^^^^^
======= ========================================
add     dns | DNS Zone Record Type | Can add DNS Zone Record Type
change  dns | DNS Zone Record Type | Can change DNS Zone Record Type
delete  dns | DNS Zone Record Type | Can delete DNS Zone Record Type
======= ========================================

Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

