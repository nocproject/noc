---
tags:
  - reference
  - api
---
# WEB Application

Представляет `API` для пользовательского интерфейса NOC'a.


## Структура приложений

В основе API лежит доработанный [Django](https://www.djangoproject.com) базовая директория - `<noc_base>/services/web` 
приложения расположены в директории `apps`, разбиты согласно **модулям** НОКа.
В директории `translations` расположены файлы перевода.

```
└── web
    ├── apps
    │   ├── aaa
    │   ├── bi
    │   ├── cm
    │   ├── crm
    │   ├── dev
    │   ├── dns
    │   ├── fm
    │   ├── gis
    │   ├── inv
    │   ├── ip
    │   ├── kb
    │   ├── main
    │   ├── maintenance
    │   ├── peer
    │   ├── phone
    │   ├── pm
    │   ├── project
    │   ├── sa
    │   ├── sla
    │   ├── support
    │   ├── vc
    │   └── wf
    └── translations
        ├── pt_BR
        └── ru
```

Директории внутри модуля представляется собой отдельные приложения, код находится в файле `views.py`. 
Это видно на примере модуля `sa`:

```
services/web/apps/sa/
├── action
│   ├── __init__.py
│   └── views.py
├── actioncommands
│   ├── __init__.py
│   └── views.py
├── administrativedomain
│   ├── __init__.py
│   └── views.py
├── authprofile
│   ├── __init__.py
│   └── views.py
...
```

Базовый класс приложений - `Application` находится в `<noc_base>/lib/app/application.py` содержит в себе 
общие методы. Приложения находится в файле `views.py`, они строятся путём наследования базового класса 
и расширяют его собственными методами `API`. Это делается через декоратор `view`:


### Шаблон пути API

Путь для методов `API` строится по следующему шаблону: `<module_name/<app_name>/<view_url>`, где:

* `<module_name>` - название директории в `apps` где находится файл `views.py`
* `<app_name>` - название директории внутри модуля
* `<view_url>` - часть, указываемая в параметре `url` декоратора `views`

### Автозагрузка приложения

При запуске сервиса `web` происходит регистрация приложений в системе. Этот механизм представлен в файле 
`lib/app/site.py` через метод `autodiscover`:

::: noc.services.web.base.site:Site.autodiscover

В нём последовательно обходятся все файлы приложений в базовой директории и добавляются в систему.

<!-- prettier-ignore -->
!!! warning
    Названия приложений должны быть уникальны, иначе при их загрузке произойдёт ошибка.

## Расширения базового класса

Написание каждого приложения с использованием базового класса достаточно трудоёмкий процесс, 
по этой причине напрямую базовый класс применяется редко. В основном используются его расширения:

* `extapplication` (`lib/app/extapplication.py`) - `API` REST интерфейс для `ExtJS` интерфейса пользователя 
* `reportapplication` (`lib/app/reportapplication.py`) - Приложение для построения `html` отчётов

Пример простого приложения, добавляет в меню пункт со ссылкой на карточку:

```python
# NOC modules
from noc.services.web.base.extapplication import ExtApplication
from noc.core.translation import ugettext as _


class KeyOutageApplication(ExtApplication):
    title = _("Cards")
    menu = "Оперативная обстановка"
    glyph = "bolt"
    link = "/api/card/view/projectoutage/%s/?refresh=100"

```

Уже на основе базовых классов расширений строятся приложения.

### ExtModelApplication и ExtDocApplication

Основной тип приложений, предоставляет `REST API` для работы основного пользовательского приложения `ExtJS`. 
Реализуют `API` для работы с моделями (или документами):

* `GET` - выводит список записей модели
* `POST`- позволяет создавать записи 
* `PUT` - изменение записи модели
* `DELETE` - удаление записи для модели

Приложение создаётся путём задания в аттрибуте `model` ссылки на модель. В качестве примера рассмотрим приложение 
`services/web/apps/sa/administrativedomain/views.py` для работы с `Action`

```python
from noc.services.web.base.extmodelapplication import ExtModelApplication, view
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.core.comp import smart_text
from noc.core.translation import ugettext as _


class AdministrativeDomainApplication(ExtModelApplication):
    """
    AdministrativeDomain application
    """

    title = _("Administrative Domains")
    menu = [_("Setup"), _("Administrative Domains")]
    model = AdministrativeDomain
    query_fields = ["name__icontains", "description__icontains"]
    lookup_default = [{"has_children": False, "id": "Leave unchanged", "label": "Leave unchanged"}]

    def field_object_count(self, o):
        return o.managedobject_set.count()

    def instance_to_lookup(self, o, fields=None):
        return {"id": o.id, "label": smart_text(o), "has_children": o.has_children}

    @view(r"^(?P<id>\d+)/get_path/$", access="read", api=True)
    def api_get_path(self, request, id):
        o = self.get_object_or_404(AdministrativeDomain, id=id)
        path = [AdministrativeDomain.objects.get(id=ns) for ns in o.get_path()]
        return {
            "data": [
                {"level": path.index(p) + 1, "id": str(p.id), "label": smart_text(p.name)}
                for p in path
            ]
        }

```

В нём объявлены место приложения в меню (`menu`) (строится относительно меню модуля), Заголовок (`title`) пункта меню 
и ссылка на модель (`model`), работа с которой осуществляется через приложение. 
Учитывая реализованные в вышестоящем классе методы для приложения будут работать следующие `API`:

* GET `sa/administrativedomain/` - вывод список `AdministrativeDomain`
* GET `sa/administrativedomain/<ID>/` - вывод информации по `AdministrativeDomain` с запрошенным идентификатором
* GET `sa/administrativedomain/lookup/` - вывод списка `AdministrativeDomain` с ограниченным набором полей (для работы списков)
* POST `sa/administrativedomain/` - создание `AdministrativeDomain`
* PUT `sa/administrativedomain/<ID>/` - изменение `AdministrativeDomain` с запрошенным идентификатором
* DELETE `sa/administrativedomain/<ID>/` - удаление `AdministrativeDomain` с запрошенным идентификатором

Помимо базовых `API` в приложении добавлен метод `sa/administrativedomain/<ID>/get_path/` для 
запроса информации о `AdministrativeDomain` с указанием его уровня в иерархии.

Также в приложении меняются аттрибуты `query_fields` и `lookup_default`, они позволяют менять поведение 
методов наследуемого класса.

### SimpleReport

Позволяет реализовывать простые отчёты, для вывода их в формате HTML страницы. 
Основная логика работы реализована в базовом классе `SimpleReport`, для построения отчёта 
достаточно реализовать метод `get_data` формирующий данные для вывода на страницу.

```python
from noc.services.web.base.simplereport import SimpleReport, PredefinedReport, TableColumn
from noc.core.translation import ugettext as _


class ReportFilterApplication(SimpleReport):
    title = _("Managed Object Profile Check Summary")
    predefined_reports = {
        "default": PredefinedReport(_("Managed Object Profile Check Summary"), {})
    }

    def get_data(self, request, report_type=None, **kwargs):

        ...
        
        data = [("1.2.2.2.2.2", _("Is Managed, objects not processed yet"), 0, "")]
        # columns = ["ID", "Value", "Percent", TableColumn(_("Detail"), format="url")]
        columns = [
            _("PP"),
            _("Status"),
            _("Quantity"),
            _("Percent"),
            TableColumn(_("Detail"), format="url"),
        ]

        return self.from_dataset(title=self.title, columns=columns, data=data)

```

Сам отчёт состоит из отдельных секций, это позволяет выводить разные виды данных в одном отчёте. 
Внутри секций доступны классы форматирования данных: 

* `TextSection` - текст
  * `SafeString` - экранирование `html`
* `TableSection` - секция таблицы
  * `TableColumn` - форматирование данных в колонке
* `SectionRow` - разделитель секций 


## Добавление приложения в Custom

