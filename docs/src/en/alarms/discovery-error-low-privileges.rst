.. _alarm-class-discovery-error-low-privileges:

==================================
Discovery | Error | Low Privileges
==================================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
CLI command is not supported in current CLI mode and nothing password for raise permission level

Probable Causes
---------------
Low permission level and not credential to raise it for execute command

Recommended Actions
-------------------
Add enable password to managed object settings or grant permission for execute commands

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
path                 Path to alarms
message              Error detail message
==================== ==================================================
