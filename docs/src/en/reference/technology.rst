.. _reference-technology:

==========
Technology
==========

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Technology is an abstraction which implies restriction
on :ref:`Resource Groups<reference-resource-group`, their *Services* and *Clients* and
their connections. Technology can be formulated as assertion

> *Services* do *technology* for *clients*

Or in simplified case, without clients

> *Services* are groupped together to do *technology*

Technology is a predicate

> *technology*(*services*, *clients*)

or

> *technology*(*services*)

Configuration
-------------

Technology settings are:

* `service_model` - Database model (i.e. `sa.ManagedObject`) used to *provide* service.
  Empty value means groupping element, not providing services
* `client_model` - Database model (like in `service_model`) used to *consume* service.
* `single_service` - *Service* resource may join only one :ref:`Resource Group<reference-resource-group>` of given technology.
* `single_client` - *Client* resource may join only one :ref:`Resource Group<reference-resource-group>` of given technology.
* `allow_children` - :ref:`Resource Group<reference-resource-group>` of given technology allows children groups and can be node of hierarchy.

Defaults
--------
NOC provides lots of *technologies* out of box. See :ref:`Technologies Reference<technologies>` for details.
