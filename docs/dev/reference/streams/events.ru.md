# Потоки events.POOL

`events.POOL` stream is a part of [Events Pipeline](index.md#events-pipeline).
Registered events are passed in unified way from various collectors
to classifier service for further analysis.

У каждого пула [Pool](../../../user/reference/concepts/pool/index.md) отдельный поток
`events`. Например пул `DEFAULT` будет использоваться поток `events.DEFAULT`,
когда пул `CORE` - поток `events.CORE`.

## Отправители

- [ping](../../../admin/reference/services/ping.md) service.
- [syslogcollector](../../../admin/reference/services/syslogcollector.md) service.
- [trapcollector](../../../admin/reference/services/trapcollector.md) service.

## Слушатели

- [classifier](../../../admin/reference/services/classifier.md) service.

## Заголовки сообшения

У потока `events` отсутствуют дополнительные заголовки.

## Формат сообщения

Потоки `events` передают сообщения закодированные в JSON.

| Поле                 | Тип                 | Описание                            |
| --------------------- | -------------------- | -------------------------------------- |
| `ts`                  | Integer              | Время регистрации события (UNIX epoch)            |
| `object`              | Integer              | Идентификатор устройства-источника (`Managed Object`)                      |
| `data`                | Object {{ complex }} | Данные сообщения                           |
| {{ tab }} `source`    | String               | Источник сообщения:                        |
|                       |                      | {{ tab }} ping                                   |
|                       |                      | {{ tab }} syslog                                 |
|                       |                      | {{ tab }} SNMP Trap                              |
| {{ tab }} `collector` | String               | Пул коллектора                            |
| {{ tab }} `message`   | String               | Сообщение `syslog`        |
| {{ tab }} `<OID>`     | String               | Переменные сообщения SNMP Trap в форматер ключ-значение |
