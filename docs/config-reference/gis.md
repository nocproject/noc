# [gis] section

Gis service configuration

## ellipsoid

|                |                     |
| -------------- | ------------------- |
| Default value  | `PZ-90`             |
| YAML Path      | `gis.ellipsoid`     |
| Key-Value Path | `gis/ellipsoid`     |
| Environment    | `NOC_GIS_ELLIPSOID` |

## enable_osm

Enable blank layer on maps.
|                |                        |
| -------------- | ---------------------- |
| Default value  | `False`                |
| YAML Path      | `gis.enable_blank`     |
| Key-Value Path | `gis/enable_blank`     |
| Environment    | `NOC_GIS_ENABLE_BLANK` |

## enable_osm

Enable OpenStreetMap layer on maps.
|                |                      |
| -------------- | -------------------- |
| Default value  | `True`               |
| YAML Path      | `gis.enable_osm`     |
| Key-Value Path | `gis/enable_osm`     |
| Environment    | `NOC_GIS_ENABLE_OSM` |

## enable_google_sat

|                |                             |
| -------------- | --------------------------- |
| Default value  | `False`                     |
| YAML Path      | `gis.enable_google_sat`     |
| Key-Value Path | `gis/enable_google_sat`     |
| Environment    | `NOC_GIS_ENABLE_GOOGLE_SAT` |

## enable_google_roadmap

|                |                                 |
| -------------- | ------------------------------- |
| Default value  | `False`                         |
| YAML Path      | `gis.enable_google_roadmap`     |
| Key-Value Path | `gis/enable_google_roadmap`     |
| Environment    | `NOC_GIS_ENABLE_GOOGLE_ROADMAP` |

## enable_tile1

Enable custom layer `tile1`.

|                |                        |
| -------------- | ---------------------- |
| Default value  | `False`                |
| YAML Path      | `gis.enable_tile1`     |
| Key-Value Path | `gis/enable_tile1`     |
| Environment    | `NOC_GIS_ENABLE_TILE1` |

## tile1_name

Set name for layer `tile1`.
|                |                      |
| -------------- | -------------------- |
| Default value  | `Custom 1`           |
| YAML Path      | `gis.tile1_name`     |
| Key-Value Path | `gis/tile1_name`     |
| Environment    | `NOC_GIS_TILE1_NAME` |

## tile1_url

Set tile url for layer `tile`.

|                |                                                      |
| -------------- | ---------------------------------------------------- |
| Default value  | `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png` |
| YAML Path      | `gis.tile1_url`                                      |
| Key-Value Path | `gis/tile1_url`                                      |
| Environment    | `NOC_GIS_TILE1_URL`                                  |

The following macroses may be used in url:

| Macro | Description                                                                                                                  |
| ----- | ---------------------------------------------------------------------------------------------------------------------------- |
| `{s}` | Expands to one of the values of `subdomains`. used sequentially to help with browser parallel requests per domain limitation |
| `{z}` | Zoom level                                                                                                                   |
| `{x}` | X coordinates                                                                                                                |
| `{y}` | Y coordinates                                                                                                                |
| `{r}` | can be used to add "@2x" to the URL to load retina tiles                                                                     |
 
|                |                            |
| -------------- | -------------------------- |
| Default value  | `[]`                       |
| YAML Path      | `gis.tile1_subdomains`     |
| Key-Value Path | `gis/tile1_subdomains`     |
| Environment    | `NOC_GIS_TILE1_SUBDOMAINS` |

## tile1_subdomains

Set subdomains for `tile1` layer. Subdomains are used sequentially to help with browser parallel requests per domain limitation.
Expands `{s}` option in `tile1_url`.

## enable_tile2

Enable custom layer `tile2`.

|                |                        |
| -------------- | ---------------------- |
| Default value  | `False`                |
| YAML Path      | `gis.enable_tile2`     |
| Key-Value Path | `gis/enable_tile2`     |
| Environment    | `NOC_GIS_ENABLE_TILE2` |

## tile2_name

Set name for layer `tile2`.
|                |                      |
| -------------- | -------------------- |
| Default value  | `Custom 2`           |
| YAML Path      | `gis.tile2_name`     |
| Key-Value Path | `gis/tile2_name`     |
| Environment    | `NOC_GIS_TILE2_NAME` |

## tile2_url

Set tile url for layer `tile`.

|                |                                                      |
| -------------- | ---------------------------------------------------- |
| Default value  | `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png` |
| YAML Path      | `gis.tile2_url`                                      |
| Key-Value Path | `gis/tile2_url`                                      |
| Environment    | `NOC_GIS_TILE2_URL`                                  |

The following macroses may be used in url:

| Macro | Description                                                                                                                  |
| ----- | ---------------------------------------------------------------------------------------------------------------------------- |
| `{s}` | Expands to one of the values of `subdomains`. used sequentially to help with browser parallel requests per domain limitation |
| `{z}` | Zoom level                                                                                                                   |
| `{x}` | X coordinates                                                                                                                |
| `{y}` | Y coordinates                                                                                                                |
| `{r}` | can be used to add "@2x" to the URL to load retina tiles                                                                     |
 
|                |                            |
| -------------- | -------------------------- |
| Default value  | `[]`                       |
| YAML Path      | `gis.tile2_subdomains`     |
| Key-Value Path | `gis/tile2_subdomains`     |
| Environment    | `NOC_GIS_TILE2_SUBDOMAINS` |

## tile2_subdomains

Set subdomains for `tile2` layer. Subdomains are used sequentially to help with browser parallel requests per domain limitation.
Expands `{s}` option in `tile2_url`.

## enable_tile3

Enable custom layer `tile3`.

|                |                        |
| -------------- | ---------------------- |
| Default value  | `False`                |
| YAML Path      | `gis.enable_tile3`     |
| Key-Value Path | `gis/enable_tile3`     |
| Environment    | `NOC_GIS_ENABLE_TILE3` |

## tile3_name

Set name for layer `tile3`.
|                |                      |
| -------------- | -------------------- |
| Default value  | `Custom 3`           |
| YAML Path      | `gis.tile3_name`     |
| Key-Value Path | `gis/tile3_name`     |
| Environment    | `NOC_GIS_TILE3_NAME` |

## tile3_url

Set tile url for layer `tile`.

|                |                                                      |
| -------------- | ---------------------------------------------------- |
| Default value  | `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png` |
| YAML Path      | `gis.tile3_url`                                      |
| Key-Value Path | `gis/tile3_url`                                      |
| Environment    | `NOC_GIS_TILE3_URL`                                  |

The following macroses may be used in url:

| Macro | Description                                                                                                                  |
| ----- | ---------------------------------------------------------------------------------------------------------------------------- |
| `{s}` | Expands to one of the values of `subdomains`. used sequentially to help with browser parallel requests per domain limitation |
| `{z}` | Zoom level                                                                                                                   |
| `{x}` | X coordinates                                                                                                                |
| `{y}` | Y coordinates                                                                                                                |
| `{r}` | can be used to add "@2x" to the URL to load retina tiles                                                                     |
 
|                |                            |
| -------------- | -------------------------- |
| Default value  | `[]`                       |
| YAML Path      | `gis.tile3_subdomains`     |
| Key-Value Path | `gis/tile3_subdomains`     |
| Environment    | `NOC_GIS_TILE3_SUBDOMAINS` |

## tile3_subdomains

Set subdomains for `tile3` layer. Subdomains are used sequentially to help with browser parallel requests per domain limitation.
Expands `{s}` option in `tile3_url`.

## tile_size

Tile size 256x256

|                |                     |
| -------------- | ------------------- |
| Default value  | `256`               |
| YAML Path      | `gis.tile_size`     |
| Key-Value Path | `gis/tile_size`     |
| Environment    | `NOC_GIS_TILE_SIZE` |
