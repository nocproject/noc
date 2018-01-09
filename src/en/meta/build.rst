==============================
NOC Documentation Build System
==============================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

This document contains direct instructions for building the NOC documentation.

Getting Started
---------------
Install Git
~~~~~~~~~~~~
Ensure Git is installed on you system

macOS
^^^^^^
macOS is supplied with Git out-of-box. You are free to use
`SourceTree <https://www.sourcetreeapp.com>`_ or any other tool of your
choices.

RHEL/Fedora/Centos
^^^^^^^^^^^^^^^^^^
.. todo::
    Describe Git installation on RHEL/Centos

Debian/Ubuntu
^^^^^^^^^^^^^
.. todo::
    Describe Git installation on Debian/Ubuntu

FreeBSD
^^^^^^^
.. todo::
    Describe Git installation on FreeBSD

Clone Documentation Repo
~~~~~~~~~~~~~~~~~~~~~~~~
First time you need to clone documentation repo

.. code-block:: sh

    $ git clone git://code.getnoc.com/noc/docs.git

Pull Changes
~~~~~~~~~~~~
To update your working copy and pull changes from repo do

.. code-block:: sh

    docs$ git pull origin master

Make Changes
~~~~~~~~~~~~
.. todo::
    Describe Git branch creating

Make changes using your favorite editor

.. todo::
    Describe changes commit

.. todo::
    Describe Git push

.. todo::
    Describe Merge Request

Automatic Builds
~~~~~~~~~~~~~~~~
NOC's GitLab CI rebuilds and deploys documentation automatically
on every push request to repository

Manual Build
------------
NOC documentation can be built manually using docker image provided.
Manual build may be used to check result before commit and push

Install Dependencies
~~~~~~~~~~~~~~~~~~~~
Docker is required for manual documentation build

macOS
^^^^^
To install Docker follow `instruction <https://docs.docker.com/docker-for-mac/>`

RHEL/Fedora/Centos
^^^^^^^^^^^^^^^^^^
.. todo::
    Describe Docker installation for RHEL/Centos

Debian/Ubuntu
^^^^^^^^^^^^^
.. todo::
    Describe Docker installation for Debian/Ubuntu

FreeBSD
^^^^^^^
.. todo::
    Describe Docker installation for Debian/Ubuntu

Attach NOC Docker Registry
~~~~~~~~~~~~~~~~~~~~~~~~~~
.. todo::
    Describe NOC docker registry attaching

Build Commands
~~~~~~~~~~~~~~
"docker-compose.yml" provided with documentation offers following commands
============= ==========================================================
Command       Description
============= ==========================================================
build         Build all documentation targets
serve         Run builtin http server and serve documentation
shell         Run shell inside build container
html          Full build of HTML documentation for all languages
html-en       Full build of english HTML documentation
html-en-inc   Fast incremental build of english HTML documentation
epub          Full build of ePub documentation for all languages
epub-en       Full build of english ePub documentation
============= ==========================================================

Full Build
~~~~~~~~~~
To run full build issue command

.. code-block:: sh

    docs$ docker-compose run --rm build

Resulting HTML will be placed into ``build/`` directory. You need
to run full build every time you adding new page

To build english HTML documentation only issue command

.. code-block:: sh

    docs$ docker-compose run --rm html-en

Incremental Build
~~~~~~~~~~~~~~~~~
Incremental build may be issued to check small changes to existing
files. It may be significantly faster as it processes only changed files

.. code-block:: sh

    docs$ docker-compose run --rm html-en-inc

Preview Result
~~~~~~~~~~~~~~
Run builtin HTTP server

.. code-block:: sh

    docs$ docker-compose up serve

And open browser at http://127.0.0.1:48888/en/
