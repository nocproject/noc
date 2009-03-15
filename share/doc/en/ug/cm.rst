************************
Configuration Management
************************
Overview
========
Configuration management. Contains generalized interface to Version Control System
to track the state and changes of the objects. Web interface allows to preview given object
for an any moment of time and to preview differences between any two moments of time.
Email notification on object changes.

Objects handled by cm:

* Device configurations
* DNS zones
* RPSL objects
* Prefix lists

cm performs two major operation: ''push'' to repository and ''pull'' from repository

Terminology
============

* Repository
* Object
* Push
* Pull

Configuration
=============

Forms
=====
Config
------
Permissions
^^^^^^^^^^^
======= ========================================
add     cm | Config | Can add Config
change  cm | Config | Can change Config
delete  cm | Config | Can delete Config
======= ========================================

DNS Objects
-----------
Permissions
^^^^^^^^^^^
======= ========================================
add     cm | DNS Object | Can add DNS Object
change  cm | DNS Object | Can change DNS Object
delete  cm | DNS Object | Can delete DNS Object
======= ========================================

Prefix Lists
------------
Permissions
^^^^^^^^^^^
======= ========================================
add     cm | Prefix List | Can add Prefix List
change  cm | Prefix List | Can change Prefix List
delete  cm | Prefix List | Can delete Prefix List
======= ========================================

RPSL Objects
------------
Permissions
^^^^^^^^^^^
======= ========================================
add     cm | RPSL Object | Can add RPSL Object
change  cm | RPSL Object | Can change RPSL Object
delete  cm | RPSL Object | Can delete RPSL Object
======= ========================================

Setup
=====
Object Notifies
---------------
Permissions
^^^^^^^^^^^
======= ========================================
add     cm | Object Notify | Can add Object Notify
change  cm | Object Notify | Can change Object Notify
delete  cm | Object Notify | Can delete Object Notify
======= ========================================

Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Reports
=======
Stale Configs (2 days)
----------------------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

IP Addresses in Config
----------------------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Latest Changes
--------------
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

