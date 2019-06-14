.. _releases-policy:

==============================
NOC Release and Tagging Policy
==============================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Branches
--------

.. _releases-policy-master:

master
^^^^^^
*master* is main development branch. *master* is protected from changes
and populated only via Merge Requests, which have passed full Q&A process.

.. _releases-policy-release-X.Y:

release-X.Y
^^^^^^^^^^^
*release-X.Y* is branch hosting whole *Release Generation*.
*Release Generation X.Y* is a group of releases, started with X.Y
and followed by X.Y.Z hotfix releases.
release-X.Y branch is protected from changes and polulated only via Merge Request,
which have passed full Q&A process.
Most of MRs on *release-X.Y* branch are *cherrypics* from MRs on *master* branch

Tags
----
Following tags are usable as tower deploy branches and Docker image tags

.. _releases-policy-latest:

latest
^^^^^^
head of :ref:`master<releases-policy-master>` branch

.. _releases-policy-latest-X.Y:

latest-X.Y
^^^^^^^^^^
head of :ref:`release-X.Y<releases-policy-release-X.Y>` branch

.. _releases-policy-X.Y:

X.Y
^^^
First release in X.Y generation on :ref:`release-X.Y<releases-policy-release-X.Y>` branch

.. _releases-policy-X.Y.Z:

X.Y.Z
^^^^^
Hotfix releases in X.Y generation on :ref:`release-X.Y<releases-policy-release-X.Y>` branch

.. _releases-stable-X.Y:

stable-X.Y
^^^^^^^^^^
Last tagged release in X.Y generation on :ref:`release-X.Y<releases-policy-release-X.Y>` branch (X.Y or last X.Y.Z)

.. _releases-stable:

stable
^^^^^^
Last tagged release in last generation
