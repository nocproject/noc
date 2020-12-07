# Technology

Technology is an abstraction which implies restriction
on [Resource Groups](../resource-group/index.md), their *Services* and *Clients* and
their connections. Technology can be formulated as assertion

> *Services* do *technology* for *clients*

Or in simplified case, without clients

> *Services* are groupped together to do *technology*

Technology is a predicate

> *technology*(*services*, *clients*)

or

> *technology*(*services*)

## Configuration

Technology settings are:

* `service_model` - Database model (i.e. `sa.ManagedObject`) used to *provide* service.
  Empty value means groupping element, not providing services
* `client_model` - Database model (like in `service_model`) used to *consume* service.
* `single_service` - *Service* resource may join only one [Resource Group](../resource-group/index.md) of given technology.
* `single_client` - *Client* resource may join only one [Resource Group](../resource-group/index.md) of given technology.
* `allow_children` - [Resource Group](../resource-group/index.md) of given technology allows children groups and can be node of hierarchy.

## Defaults
NOC provides lots of *technologies* out of box. See Technologies Reference for details.
