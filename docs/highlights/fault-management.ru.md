# Управление неисправностями

Управление неисправностями - это процесс сбора и обработки входящих событий, поступающих из различных источников. NOC предоставляет гибкий конвейер обработки событий, разделенный на четко разграниченные этапы:

* _Сбор_ - сбор событий из внешних источников, таких как Syslog, SNMP Trap, активные проверки, пороги метрик и их внедрение в конвейер обработки событий.
* _Классификация_ - удаление всех зависимых от устройства характеристик и их замена обобщенными [классами событий](../concepts/event-class/index.md). NOC распознает около 300 классов событий из коробки.
* _Корреляция_ - анализ возможных событий открытия и закрытия тревог, корреляция на основе правил, корреляция на основе топологии, поднятие и снятие тревог, расчет влияния на обслуживание.
* _Эскалация_ - обработка тревог на основе правил, уведомление и эскалация во внешние системы учета неисправностей.

Каждый этап обрабатывается разным набором [микросервисов](microservices.md), что позволяет настраивать количество рабочих в соответствии с текущей нагрузкой. Многоэтапная обработка позволяет сосредотачивать персонал мониторинга только на актуальных проблемах, которые вызывают деградацию обслуживания.

# См. также

* [Fault Management](../fault-management/index.md)