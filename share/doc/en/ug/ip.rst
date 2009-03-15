************************
Address Space Management
************************
Overview
========
IP Address Management. Manages allocation and suballocations for peer module AS objects.
suballocations can be nested to any required level. Supports multi-VRF address space management.
Contains database of allocated prefixes and IP addresses. Controls address space allocation and usage

Terminology
============
* Allocation
* Suballocation
* VRF

Forms
=====
Assigned addresses
------------------
Permissions
^^^^^^^^^^^
======= ========================================
add     ip | IPv4 Block | Can add IPv4 Block
change  ip | IPv4 Block | Can change IPv4 Block
delete  ip | IPv4 Block | Can delete IPv4 Block
======= ========================================

Setup
=====
VRF Groups
----------
Permissions
^^^^^^^^^^^
======= ========================================
add     ip | VRF Group | Can add VRF Group
change  ip | VRF Group | Can change VRF Group
delete  ip | VRF Group | Can delete VRF Group
======= ========================================

VRFs
----
Permissions
^^^^^^^^^^^
======= ========================================
add     ip | VRF | Can add VRF
change  ip | VRF | Can change VRF
delete  ip | VRF | Can delete VRF
======= ========================================

Block Access
------------
Permissions
^^^^^^^^^^^
======= ========================================
add     ip | IPv4 Block Access | Can add IPv4 Block Access
change  ip | IPv4 Block Access | Can change IPv4 Block Access
delete  ip | IPv4 Block Access | Can delete IPv4 Block Access
======= ========================================

Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Reports
=======
IP Block summary
----------------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Allocated Blocks
----------------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Free Blocks
-----------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

