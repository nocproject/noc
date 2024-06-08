# How to Create Equipment Facades

Facades are a visual representation of equipment and display its physical configuration and port layout. They are attached to object models and can be front and rear (only for chassis).

## Facade Naming Rules

### Connection Types

The beginning of the facade name for connection types should match the type name. Then, one of two suffixes should be specified:

* `(M)` - for "male"
* `(F)` - for "female"

### Object Model

* The name of the front facade matches the model name completely.
* The name of the rear facade starts with the model name, followed by a space and the `(Rear)` suffix.

## Facade Requirements

Facades are created in SVG format, following common conventions:

* All dimensions are specified in millimeters; fractional values are allowed.
* SVG must contain a viewBox attribute in the form "0 0 WIDTH HEIGHT", where WIDTH and HEIGHT are the dimensions in millimeters.
* To avoid confusion, coordinates and sizes of elements inside SVG should also be specified in millimeters.
* If an element is a filled rectangle, the stroke width parameter must be set to 0; otherwise, the element will protrude by half the stroke width in each direction.
* Parts of the facade related to a specific connection must have an `id` attribute in the form of `noc-slot-<normalized name>` (created automatically in templates).

## Connection Type Preparation

Connection types can include up to two facades - one for each gender. Connection type facades are not used by themselves but are used as template elements on equipment facades.

Additionally, the dimensions of module slot rectangles are also specified in connection type data:

| Interface    | Attribute | Description  |
| ------------ | --------- | ------------ |
| `dimensions` | `width`   | Width in mm  |
| `dimensions` | `height`  | Height in mm |

See the [dimensions](../model-interfaces-reference/dimensions.md) interface description for additional details.

Then, on the templates, slots for modules and cards will immediately have the required dimensions. Since connection types are often reused, correctly specified attributes will allow generating templates for the entire module lineup.

## Object Model Preparation

Front and rear facades can be attached to the object model. To properly generate a facade template, its dimensions must be specified. They are set through model parameters in one of two ways.

For rack-mounted equipment:

| Interface   | Attribute | Description   |
| ----------- | --------- | ------------- |
| `rackmount` | `units`   | Size in units |

The necessary dimensions will be calculated automatically.
See the [rackmount](../model-interfaces-reference/rackmount.md) interface description for additional details.

For other equipment (modules, power supplies), if there is a connection type of `o`, the dimensions of the connection type are used.

For standalone non-rack equipment, dimensions are set in attributes:

| Interface    | Attribute | Description  |
| ------------ | --------- | ------------ |
| `dimensions` | `width`   | Width in mm  |
| `dimensions` | `height`  | Height in mm |

See the [dimensions](../model-interfaces-reference/dimensions.md) interface description for additional details.

## Obtaining a Template

In {{ ui_path("Inventory", "Setup", "Object Model") }}, select the model. Next to the `Front` or `Rear Facade` fields, click the `Template` button. As a result, a template containing the necessary elements will be downloaded.

## Editing Tools

The SVG editor must allow editing coordinates and sizes in numerical form.

Recommended:

* [BoxySVG](https://boxy-svg.com)

## Uploading a Facade

After the image is prepared, go to {{ ui_path("Inventory", "Setup", "Facade") }} and click `Add`.

Next, fill in the `Name` field according to the "Facade Naming Rules" section.

Then, in the `Data` field, click the `Upload` button and select the file.

After the file is uploaded, its image will appear in the field.

Then click `Save`.

## Attaching Facades to Connection Types

In {{ ui_path("Inventory", "Setup", "Connection Type") }}, select the connection type.

Then, in the `Male Facade` and `Female Facade` fields, select the required facades from the drop-down list.

To save the changes, click `Save`.

## Attaching Facades to Object Models

In {{ ui_path("Inventory", "Setup", "Object Models") }}, select the model.

Next, in the `Front Facade` and `Rear Facade` fields, select the required facades from the drop-down list.

To save the changes, click `Save`.

To check the facade after saving, reopen the model and analyze the first column in the Connections field.

* The "finger right" icon indicates that the slot is present on the front facade.
* The "finger left" icon indicates that the slot is present on the rear facade.

## Reusing Facades

Often, equipment from one vendor with a similar port configuration has the same external appearance. In this case, facades can be used by multiple models, provided they have connections with the same names.

## Placing Facades in NOC Collections

See the [Sharing collections HOWTO](../sharing-collections-howto/index.md) section for a description of the process of submitting changes to NOC project collections.
