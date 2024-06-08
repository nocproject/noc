# Обзор NBI

NBI основан на [Northbound Interface](https://en.wikipedia.org/wiki/Northbound_interface).
Это интерфейс для систем вернхнего уровня, желающих взаимодействовать с НОКом для выполнения собственных задач.

НОК предоставляется простой HTTP REST API, используя JSON как транспортный формат. Авторизация выполняется 
через ключи [API Keys](../concepts/apikey/index.md). 

## API

| Name                                  | Base Path                   | API Access            | Назначение                                                                         |
| ------------------------------------- | --------------------------- | --------------------- | ---------------------------------------------------------------------------------- |
| [config](config.md)                   | `/api/nbi/config/`          | `nbi:config`          | Запрос конфигурации устройства                                                     |
| [configrevisions](configrevisions.md) | `/api/nbi/configrevisions/` | `nbi:configrevisions` | Запрос списка версии конфигурации устройства                                       |
| [getmappings](getmappings.md)         | `/api/nbi/getmappings/`     | `nbi:getmappings`     | Запрос привязки идентификатора устройства к внешним системам (и обратная операция) |
| [objectmetrics](objectmetrics.md)     | `/api/nbi/objectmetrics/`   | `nbi:objectmetrics`   | Запрос метрик устройства                                                           |
| [objectstatus](objectstatus.md)       | `/api/nbi/objectstatus/`    | `nbi:objectstatus`    | Запрос доступности устройства                                                      |
| [path](path.md)                       | `/api/nbi/path/`            | `nbi:path`            | Запрос пути по топологии между двумя устройствами или интерфейсами                 |
| [telemetry](telemetry.md)             | `/api/nbi/telemetry/`       | `nbi:telemetry`       | Отправка метрик в НОК                                                              |
