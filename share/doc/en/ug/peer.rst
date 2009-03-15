******************
Peering Management
******************
Overview
========
Peering management. Contains database of major peering objects:

* Maintainers
* Persons
* Autonomous systems
* AS-Sets
* BGP peers 
* Communities

Generates valid RPSL representation for database objects.
Generates optimized BGP filters. Provides integrated looking glass for debugging purposes.
RPSL representation and prefix-lists are stored in cm repo to track changes.

Terminology
============
* RPSL
* Peering Point
* import filter
* export filter

Forms
=====
ASes
----
Permissions
^^^^^^^^^^^
======= ========================================
add     peer | AS | Can add AS
change  peer | AS | Can change AS
delete  peer | AS | Can delete AS
======= ========================================

ASsets
------
Permissions
^^^^^^^^^^^
======= ========================================
add     peer | ASSet | Can add ASSet
change  peer | ASSet | Can change ASSet
delete  peer | ASSet | Can delete ASSet
======= ========================================

Communities
-----------
Permissions
^^^^^^^^^^^
======= ========================================
add     peer | Community | Can add Community
change  peer | Community | Can change Community
delete  peer | Community | Can delete Community
======= ========================================

Peering Points
--------------
Permissions
^^^^^^^^^^^
======= ========================================
add     peer | Peering Point | Can add Peering Point
change  peer | Peering Point | Can change Peering Point
delete  peer | Peering Point | Can delete Peering Point
======= ========================================

Peers
-----
Permissions
^^^^^^^^^^^
======= ========================================
add     peer | Peer | Can add Peer
change  peer | Peer | Can change Peer
delete  peer | Peer | Can delete Peer
======= ========================================

Setup
=====
Community Types
---------------
Permissions
^^^^^^^^^^^
======= ========================================
add     peer | Community Type | Can add Community Type
change  peer | Community Type | Can change Community Type
delete  peer | Community Type | Can delete Community Type
======= ========================================

RIRs
----
Permissions
^^^^^^^^^^^
======= ========================================
add     peer | RIR | Can add RIR
change  peer | RIR | Can change RIR
delete  peer | RIR | Can delete RIR
======= ========================================

Persons
-------
Permissions
^^^^^^^^^^^
======= ========================================
add     peer | Person | Can add Person
change  peer | Person | Can change Person
delete  peer | Person | Can delete Person
======= ========================================

Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

