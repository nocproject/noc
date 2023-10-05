# Интеграция

ИТ-инфраструктуры в сфере телекоммуникаций обычно становятся очень сложными, и сложно представить, чтобы одна система могла бы охватить все процессы и задачи. NOC охватывает следующие области:

* Инвентаризация сетевых ресурсов (NRI)
* Управление IP-адресами (IPAM)
* Управление авариями (FM)
* Управление производительностью (PM)
* Управление конфигурацией (CM)
* Активация услуг (SA)

NOC разработан так, чтобы взаимодействовать с другими системами и предоставлять API для интеграции с соседними системами:

* Extract-Transfer-Load (ETL) для импорта данных из внешних систем NRI. NOC способен синхронизировать данные с несколькими системами NRI.
* API интеграции с системами учета инцидентов (TT) для эскалации тревожных сигналов во внешнюю систему учета инцидентов. NOC может проводить эскалацию в несколько систем учета инцидентов в зависимости от настроек политики.
* [API потоков данных](../datastream-api-reference/index.md) - высокопроизводительный экспорт данных практически в реальном времени во внешние системы. NOC может собирать и предоставлять актуальное состояние сети для внешнего анализа и обработки.
* North-bound Interface (NBI) - предоставляет широкий набор функций NOC для внешних систем.
* API аутентификации - позволяет интегрировать установку NOC с существующими системами AAA, такими как Active Directory (AD), LDAP, RADIUS. NOC способен аутентифицироваться в нескольких системах.
* API внешнего хранения - позволяет загружать конфигурации устройств во внешние хранилища с использованием протоколов FTP, SCP, S3.

API интеграции NOC широко используется для моделирования, управления качеством данных (DQM), согласования данных (DR), управления качеством услуг (SQM).