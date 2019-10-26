.. _release-19.4:

========
NOC 19.4
========

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

.. warning::

    Upcoming release.

Highlights
----------
DataStream improvements
^^^^^^^^^^^^^^^^^^^^^^^
:ref:`managedobject DataStream<api-datastream-managedobject>` got
additional `tags` attribute exposing ManagedObjects's tags. Tags allow
to pass unstructured metadata to external system.

Development Process Changes
---------------------------

Code Formatting
^^^^^^^^^^^^^^^

NOC adopts `Prettier <https://prettier.io/>`_ for JS, JSON, CSS and YAML code formatting.
CI pipeline checks code formatting of changed files. Any misformatting considered the error
and CI pipeline fails at the `lint` stage. We recommend to
add Prettier formatting to git's pre-commit hook or to the IDE's on-save
hook.

Docker container is also available. Use::

    docker run --rm \
        -w /src \
        -v $PWD:/src \
        registry.getnoc.com/infrastructure/prettier:master \
        /usr/local/bin/prettier --config=.prettierrc --write <file name>

to format file
