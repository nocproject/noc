# Card

These are `ReadOnly` (*non-editable*) custom user interfaces consisting of static HTML pages. The underlying technology is the [Jinja](https://jinja.palletsprojects.com) template engine and a data generator class for the `environment`. They have the following advantages compared to the basic user interface:

* Intended for reading only
* Faster rendering speed
* Works even on very old browser versions
* Allows link exchange thanks to accessibility via `URL`

The base directory is `<noc>/services/card/` and has the following structure:

```
services/
└──card
    ├── cards
    └── templates
    └── translations
        ├── pt_BR
        └── ru

```

Here is an explanation of the directory contents:

- **cards**: This directory contains the backend code for generating variables used in the `environment` of the template engine.

- **templates**: This directory contains HTML templates used to create card pages. The template files have the extension `<template_name>.html.j2`.

- **translations**: This directory stores translation strings.

!!! note

    For simplicity, we will refer to the card's backend as simply the "card" in the text below.

## Card File

The base class for a card is `BaseCard`, located in the `cards/base.py` file. Cards should inherit from this base class. 
It is mandatory to implement the `get_data` method, which returns a set of variables for use in the template of the card page. 
Additionally, attributes such as `name` (unique name for the card), `default_template_name` (the name of the card's template), and `model` (a reference to the data model the card works with) should be filled in.

To access a card, the URL is formed in the following format: `<root>/<card_name>/<ID>/`, where:

- `<root>` is the base URL of the NOC system.
- `<card_name>` is the name of the card specified in the `name` attribute.
- `<ID>` is the identifier of the requested data. If the `model` is filled in, a search for an instance is performed based on the identifier. If the search fails, a "Not Found" page is displayed.

Useful methods in the `BaseCard` class:

- `get_object`: This method is responsible for searching for the specified `<ID>`. It can be useful to override it if you need to search by multiple identifiers.
- `RedirectError`: This error class performs a redirection to the specified `URL`.
- `NotFoundError`: This method returns a "404" page. By default, it is opened if the object cannot be found based on the `<ID>`.

Here is an example of a simple card for the `Firmware` model, where an instance of `Firmware` is returned as data.

Card File:

```python

from noc.inv.models.firmware import Firmware
from .base import BaseCard  # Base class


class FirmwarePlanCard(BaseCard):
    name = "firmware"  # Card's name
    default_template_name = "firmware"  # default template name
    model = Firmware  # Used model

    def get_data(self):  # Build template context
        # return {"object": self.object}
        ...
```

As seen in this card, it displays information about a specific instance, which is a common use case for cards.

Now, let's explore some special use cases for cards:

### Cards Without Data Models

In addition to cards that display data from specific models, cards can also be implemented that are not associated with any particular data model. In such cases, the `model` attribute is left empty. Examples of such cards include `outage` and `path` cards.

The `path` card, for instance, is used to visualize the geographical path between a pair of `ManagedObjects`.

```python

class PathCard(BaseCard):
    name = "path"
    default_template_name = "path"
    card_css = ["/ui/pkg/leaflet/leaflet.css", "/ui/card/css/path.css"]
    card_js = ["/ui/pkg/leaflet/leaflet.js", "/ui/card/js/path.js"]

    def get_data(self):
        ...
        return {"mo1": mo1, "mo2": mo2, "path": smart_text(orjson.dumps(path))}
```

In the example, you can see the use of the `leaflet` library for rendering a geographic map in addition to the `path` module that implements functionality in JavaScript.

### Cards Implemented via Ajax

In some cases, there is a need to generate dynamic content via an API instead of creating static HTML. In such cases, the data returned is generated through the `get_ajax_data` method. An example of such a card is the `alarmheat` card found in `cards/alarmheat.py`.

```python

class AlarmHeatCard(BaseCard):
    name = "alarmheat"
    card_css = ["/ui/pkg/leaflet/leaflet.css", "/ui/card/css/alarmheat.css"]
    card_js = [
        "/ui/pkg/leaflet/leaflet.js",
        "/ui/pkg/leaflet.heat/leaflet-heat.js",
        "/ui/card/js/alarmheat.js",
    ]

    default_template_name = "alarmheat"

    _layer_cache = {}
    TOOLTIP_LIMIT = config.card.alarmheat_tooltip_limit

    def get_data(self):
        return {
            "maintenance": 0,
            "lon": self.current_user.heatmap_lon or 0,
            "lat": self.current_user.heatmap_lat or 0,
            "zoom": self.current_user.heatmap_zoom or 0,
        }

    def get_ajax_data(self, **kwargs):

        zoom = int(self.handler.get_argument("z"))
        west = float(self.handler.get_argument("w"))
        east = float(self.handler.get_argument("e"))

        ...

        return {
            "alarms": alarms,
            "summary": self.f_glyph_summary({"service": services, "subscriber": subscribers}),
            "links": links,
            "pops": points,
        }

```

In this card, the get_ajax_data method is implemented, and access to the arguments is directly available from the data generation method.