# Custom (Расширение)

  NOC предоставляет широкие возможности по расширению функционала системы путём добавления собственного кода. 
Это позволяет менять поведение системы в широких пределах и компенсировать недостаточный функционал.


## Список поддерживаемых расширений 

Поддерживаются следующие расширения для системы

* `bi` - Модели для `BI`
* `cmibs` - Файлы `cmibs`
* `commands` - инструментарий команд
* `collections` -
* `geocoder` - GIS геокодеры для внешних систем 
* `etl`
  * `extractors` - `ETL` адаптеры для внешних систем
  * `loader` - собственные загрузчики
  * `portmappers` - адаптеры привязки интерфейсов с внешними системами
* `handlers` - директория с обработчиками [Handlers](../../reference/handlers/index.md)
* `sa` - профили оборудования
  * `profiles` - Профили SA [SA Profile](../../background/sa-profile/index.md)
  * `interfaces` - Интерфейсы SA [SA Interface](../../background/sa-profile/index.md#Интерфейсы_SA)
* `services` - расширения сервисов системы
  * `card` - пользовательские карточки [Card](../../reference/card/index.md)
  * `web` - пользовательские веб приложения [Web](../../reference/web/index.md)
  * `nbi` - NBI API endpoint [NBI](../../reference/api/nbi/index.md)
* `templates` - `Jinja` шаблоны для различных частей системы
  * `ddash` - шаблоны для графиков метрик `PM` 
* `tt` - адаптеры для систем эскалации аварии (`TroubleTicket`)


## Структура custom

Расширения хранятся отдельно от основного кода и динамически подгружаются системой при старте. Основное требование - расширение должно занимать 
определённое место в структуре файловой системы. Корневая директория для расширения задаётся черезе настройку `custom_path` в 
разделе `path` глобальной конфигурации [Custom Path](../../../admin/reference/config/path.md#custom_path). 
Настройка производится при установке системы в башне `Tower`, по умолчанию размещается в `/opt/noc_custom`, 
cтруктура выглядит следующим образом:

```
.
├── bi
│   └── models
├── cmibs
├── collections
│   ├── fm.alarmclasses
│   └── sa.profiles
├── commands
├── core
│   └── geocoder
├── etl
│   ├── bi
│   ├── extractors
│   ├── loader
│   └── portmappers
├── handlers
│   ├── alarms
├── lib
│   └── app
├── sa
│   ├── interfaces
│   └── profiles
├── services
│   ├── card
│   ├── nbi
│   └── web
├── templates
│   └── ddash
└── tt

```

<!-- prettier-ignore -->
!!! note
    Для подхватывания изменений в кастоме обязателен перезапуск процесса (или всего НОКа)