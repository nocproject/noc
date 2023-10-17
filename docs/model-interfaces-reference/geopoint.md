# geopoint Model Interface

`geopoint` interface allows to position object on map. An object with the `geopoint`
interface will be shown on maps's layer named `layer` starting from `zoom` level.

`zoom` level settings can ovrerride layer's defaults.

## Variables

<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `layer` | str | Map layer code | {{ yes }} | {{ yes }} |
| `srid` | str | Spatial reference system, autority:code or LOCAL | {{ yes }} | {{ no }} |
| `zoom` | int | Default zoom level (override layer's default) | {{ no }} | {{ no }} |
| `x` | float | x coordinate, in SRS units | {{ yes }} | {{ no }} |
| `y` | float | y coordinate, in SRS units | {{ yes }} | {{ no }} |
| `z` | float | Height above ellipsoid, in meters | {{ no }} | {{ no }} |
| `angle` | float | Rotation angle, in degrees | {{ no }} | {{ no }} |

<!-- table end -->

Examples of Spatial reference systems:

| srid                                                    | Description                |
| ------------------------------------------------------- | -------------------------- |
| [EPSG:4326](http://spatialreference.org/ref/epsg/4326/) | GPS                        |
| [SR-ORG:95](http://spatialreference.org/ref/sr-org/95/) | Google Maps/Microsoft Live |


## Examples

```json
{
  "geopoint": {
    "layer": "pop_regional"
  }
}
```
