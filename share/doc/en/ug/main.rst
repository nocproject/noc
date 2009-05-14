****
Main
****
Overview
========
Main module is a core or noc. Main module provides following services:

* Core system services
* Database access, migration and backup tools
* User authentication and authorization
* Online documentation access
* Global search
* Reporting engine

Terminology
============
Forms
=====
Setup
=====
Users
-----
Permissions
^^^^^^^^^^^
======= ========================================
add     auth | user | Can add user
change  auth | user | Can change user
delete  auth | user | Can delete user
======= ========================================

Groups
------
Permissions
^^^^^^^^^^^
======= ========================================
add     auth | group | Can add group
change  auth | group | Can change group
delete  auth | group | Can delete group
======= ========================================

Languages
---------
Permissions
^^^^^^^^^^^
======= ========================================
add     main | Language | Can add Language
change  main | Language | Can change Language
delete  main | Language | Can delete Language
======= ========================================

MIME Types
----------
Database of file extension to MIME type mappings.
Used to set up valid Content-Type for downloadable
files and attachments (i.e. Knowledge Base attachments)

Permissions
^^^^^^^^^^^
======= ========================================
add     main | MIME Type | Can add MIME Type
change  main | MIME Type | Can change MIME Type
delete  main | MIME Type | Can delete MIME Type
======= ========================================

Configs
-------
Configuration files editor.

Permissions
^^^^^^^^^^^
======= ========================================
change  Superuser
======= ========================================

Documentation
=============
Administrator's Guide
---------------------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

User's Guide
------------
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

Reports
=======
Backups Status
--------------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Lines of code
-------------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

System version
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

Periodic Tasks
==============
main.backup
-----------

main.cleanup_sessions
---------------------
