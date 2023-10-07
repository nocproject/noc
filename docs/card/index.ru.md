# Card  (Карточка)

Представляют собой `ReadOnly` (*без возможности редактирования*) пользовательский интерфейс состоящий из статичных HTML страниц. 
В основе которого шаблонизатор [Jinja](https://jinja.palletsprojects.com) и класс-генератор данных для `environment`. 
Обладает следующими преимуществами по сравнению с базовым интерфейсом пользователья:

* Предназначен только для чтения
* Более высокая скорость отрисовки
* Работает даже на очень старых версиях браузеров
* Благодаря доступность черезе `URL` позволяет организовать обмен ссылками

Базовой директории является `<noc>/services/card/`, представляет собой следующую структуру:

```
services/
└──card
    ├── cards
    └── templates
    └── translations
        ├── pt_BR
        └── ru

```

В директориях представлено следующее содержимое:

* **cards** *бэкэнд* генератор переменных для `environment` шаблонизатора
* **templates** Шаблон HTML для формирования страницы карточки. Файл с расширением `<template_name>.html.j2`
* **translations** - строки перевода

<!-- prettier-ignore -->
!!! note
    Для простоты дальше по тексту бэкэнд карточки будем называть *карточка*

## Файл карточки

Базовый класс карточки - `BaseCard` расположен в файле `cards/base.py`, карточки должны наследовать от него. 
Обязательными к реализации является метод `get_data`, возвращающий набор переменных для использования в шаблоне страницы 
и заполнение аттрибутов `name` - имя карточки (должно быть уникальным) и `default_template_name` - имя шаблона карточки, 
`model` - ссылка на модель данных с которой работает карточка.

Для вызова карточки формируется URL вида `<root>/<card_name>/<ID>/`, где:

* `<root>` - базовый URL НОКа
* `<card_name>` - имя карточки, указанное в аттрибуте `name`
* `<ID>` - идентификатор запрашиваемых данных, в случае заполненного `model`, будет произведён поиск инстанса по идентификатору. Если поиск не удался - будет выдана страница `Not Found`

Полезные методы класса `BaseCard`:

* `get_object` - в нём происходит поиск переданного `<ID>`, может быть полезно переопределить если необходим поиск по нескольким идентификаторам
* `RedirectError` - класс ошибки делает переадресацию на заданный `URL`
* `NotFoundError` - возвращает страницу `404`. По умолчанию открывается если не удалось найти объект по идентификатору `<ID>`


Пример простой карточки по модели `Firmware`, в качестве данных возвращается инстанс `Firmware`

Файл карточки:

```python

from noc.inv.models.firmware import Firmware
from .base import BaseCard  # Базовый класс


class FirmwarePlanCard(BaseCard):
    name = "firmware"  # Имя карточки
    default_template_name = "firmware"  # Имя шаблона по умолчанию
    model = Firmware  # Ссылка на модель

    def get_data(self):  # Формирование данных для шаблонизатора
        # return {"object": self.object}
        ...


```

Как видно в данной карточке выводится информация о конкретном инстансе. Это часто встречающаяся использование карточек. 


Рассмотрим несколько особых случаев использования карточек

### Карточки без модели данных

Помимо карточек с данными какой-либо модели, могут быть реализованы карточки не связанные с данными какой-либо конкретной модели. В этом случае аттрибут `model` не заполняется. Примерами таких карточек являются `outage` и `path`.

Карточка `path` вывод на географическую карту путь между парой `ManagedObject`

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

На примере можно видеть использование библиотеки `leaflet` для отрисовки географической карты в дополнение модуля `path` реализующего функционал в `JavaScript`.


### Карточки реализованные через Ajax

В некоторых случаях есть необходимость формировать динамическое наполнение через `API` вместо формирования статического HTML. В этом случае отдаваемые данные формируются через метод `get_ajax_data`. Примером такой карточки служит `alarmheat` - `cards/alarmheat.py`:

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

В данной карточке реализован метод `get_ajax_data`, и доступ к аргументам непосредственно из метода формирования данных.
