===========================
NOC Manual Organization
===========================

This document provides an overview of the global organization of the
documentation resource. Refer to the notes below if you are having
trouble understanding the reasoning behind a file's current location,
or if you want to add new documentation but aren't sure how to
integrate it into the existing resource.

If you have questions, don't hesitate to open a ticket in the
`Documentation GitLab Project <https://code.getnoc.com/noc/docs/issues>`_.

.. todo::

    Describe documentation telegram channel

Global Organization
-------------------

Indexes and Experience
~~~~~~~~~~~~~~~~~~~~~~
The documentation project has two "index files": ``/contents.rst`` and
``/index.rst``. The "contents" file provides the documentation's tree structure,
which Sphinx uses to create the left-pane navigational structure,
to power the "Next" and "Previous" page functionality,
and to provide all overarching outlines of the resource.
The *index* file is not included in the "contents" file (and
thus builds will produce a warning here) and is the page that users
first land on when visiting the resource.

Having separate "contents" and "index" files provides a bit more
flexibility with the organization of the resource while also making it
possible to customize the primary user experience.

Topical Organization
~~~~~~~~~~~~~~~~~~~~
The placement of files in the repository depends on the *type* of
documentation rather than the *topic* of the content. Like the
difference between ``contents.rst`` and ``index.rst``, by decoupling
the organization of the files from the organization of the information
the documentation can be more flexible and can more adequately address
changes in the product and in users' needs.

*Files* in the ``src/`` directory represent the tip of a logical
tree of documents, while *directories* are containers of types of
content. There is only one level of sub-directories in the ``src/``
directory
