.. _dev-tools:

=====
Tools
=====

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

.. _dev-tools-pycharm:

PyCharm IDE
-----------
NOC DevTeam leverages `PyCharm IDE <https://www.jetbrains.com/pycharm/>`_
gracefully provided by `JetBrains <https://www.jetbrains.com/>`_
under the terms of `OpenSource Support Program <https://www.jetbrains.com/community/opensource/>`_.

.. _dev-tools-pycharm-flake8:

flake8
^^^^^^
NOC CI uses `flake8 <http://flake8.pycqa.org/en/latest/>`_ to enforce code style.

To set up flake8 external tool select
:guilabel:`Preferences` > :guilabel:`Tools` > :guilabel:`External Tools`.
Press :guilabel:`+` button. Fill the form:

* :guilabel:`Name`: `flake8`
* :guilabel:`Program`: `/usr/local/bin/docker`
* :guilabel:`Arguments`: `run --rm -w /src -v $ProjectFileDir$:/src registry.getnoc.com/infrastructure/noc-py-lint:master /usr/local/bin/flake8 $FileDirRelativeToProjectRoot$/$FileName$`
* :guilabel:`Working Directory`: `$ProjectFileDir$`
* :guilabel:`Open console for tool output`: Check

Press :guilabel:`Ok`

To check current file select
:guilabel:`Tools` > :guilabel:`External Tools` > :guilabel:`flake8`

.. _dev-tools-pycharm-black:

black
^^^^^
NOC uses `black <https://black.readthedocs.io/en/stable/>`_ for automatic code
formatting and codestyle enforcing.

To set up black external tool select
:guilabel:`Preferences` > :guilabel:`Tools` > :guilabel:`External Tools`.
Press :guilabel:`+` button. Fill the form:

* :guilabel:`Name`: `black format`
* :guilabel:`Program`: `/usr/local/bin/docker`
* :guilabel:`Arguments`: `run --rm -w /src -v $ProjectFileDir$:/src registry.getnoc.com/infrastructure/noc-py-lint:master /usr/local/bin/black $FileDirRelativeToProjectRoot$/$FileName$`
* :guilabel:`Working Directory`: `$ProjectFileDir$`
* :guilabel:`Open console for tool output`: Check

Press :guilabel:`Ok`

To format current file select
:guilabel:`Tools` > :guilabel:`External Tools` > :guilabel:`black format`
