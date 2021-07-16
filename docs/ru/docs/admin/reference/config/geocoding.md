# [geocoding] section

Geocoding service configuration

## order

|                |                       |
| -------------- | --------------------- |
| Default value  | `yandex,google`       |
| YAML Path      | `geocoding.order`     |
| Key-Value Path | `geocoding/order`     |
| Environment    | `NOC_GEOCODING_ORDER` |

## yandex_key

|                |                            |
| -------------- | -------------------------- |
| Default value  | ``                         |
| YAML Path      | `geocoding.yandex_key`     |
| Key-Value Path | `geocoding/yandex_key`     |
| Environment    | `NOC_GEOCODING_YANDEX_KEY` |

## yandex_apikey

|                |                               |
| -------------- | ----------------------------- |
| Default value  | ``                            |
| YAML Path      | `geocoding.yandex_apikey`     |
| Key-Value Path | `geocoding/yandex_apikey`     |
| Environment    | `NOC_GEOCODING_YANDEX_APIKEY` |

## google_key

|                |                            |
| -------------- | -------------------------- |
| Default value  | ``                         |
| YAML Path      | `geocoding.google_key`     |
| Key-Value Path | `geocoding/google_key`     |
| Environment    | `NOC_GEOCODING_GOOGLE_KEY` |

## google_language

|                |                                 |
| -------------- | ------------------------------- |
| Default value  | `en`                            |
| YAML Path      | `geocoding.google_language`     |
| Key-Value Path | `geocoding/google_language`     |
| Environment    | `NOC_GEOCODING_GOOGLE_LANGUAGE` |

## negative_ttl

Period then saving bad result

|                |                              |
| -------------- | ---------------------------- |
| Default value  | `7d`                         |
| YAML Path      | `geocoding.negative_ttl`     |
| Key-Value Path | `geocoding/negative_ttl`     |
| Environment    | `NOC_GEOCODING_NEGATIVE_TTL` |
