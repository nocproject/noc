---
template: index.html
title: NOC
hide:
  - navigation
  - toc
hero:
  title: Проект NOC
  subtitle: NOC - масштабируемая, высокопроизводительная и система управления сетью с открытым исходным кодом для поставщиков интернет-услуг и контент-поставщиков
  install_button: Начало работы
  source_button: Исходный код
highlights:
  - title: Discovery
    description: >
      Продвинутое обнаружение топологии сети через несколько протоколов,
      включая конфигурацию и использование ресурсов. Оно обеспечивает синхронизацию между
      вашим инвентарем и реальным состоянием сети, обеспечивая точные знания и контроль.
    link: discovery
  - title: Inventory
    description: >
      Централизованная база данных физических и логических ресурсов.
      Отслеживает физические активы, такие как шасси и модули. Отслеживает
      использование логических ресурсов (IP, VLAN, номера телефонов) также.
      Планирование IP-адресов через IPAM
    link: inventory
  - title: Configuration Management
    description: >
      Оптимизирует управление конфигурацией сети. Автоматизирует резервное копирование, отслеживает изменения,
      и обеспечивает соответствие. С функциями версионирования и отката, упрощает обновления,
      улучшая надежность и безопасность сети.
    link: configuration-management
  - title: Fault Management
    description: >
      Анализ причины неисправности, корреляция топологии, эскалация.
      Активное зондирование и обнаружение условий пассивной тревоги
      в системных журналах и SNMP-ловушках.
    link: fault-management
  - title: Performance Management
    description: >
      Гибкий сбор метрик с использованием SNMP и CLI.
      Долгосрочное хранение метрик. Автоматическая настройка панелей.
      Сложное управление порогами с использованием оконных функций.
    link: performance-management
  - title: Service Activation
    description: >
      Простое взаимодействие с устройством через telnet,
      SSH, веб, TL1, MML и SNMP для безшовной активации услуг.
    link: service-activation
  - title: Network Automation
    description: >
      Разблокируйте потенциал сетевой автоматизации с нашей обширной структурой,
      оснащенной простым в использовании Python API. Оптимизируйте задачи, оркестрируйте процессы,
      и достигайте большей эффективности в управлении вашей сетевой инфраструктурой.
    link: network-automation
  - title: Integration
    description: >
      Прекрасно сотрудничает с другими системами. NOC является частью вашей инфраструктуры.
      Интерфейс ETL позволяет импортировать данные из существующих систем.
      API DataStream и интерфейсы NBI предоставляют услуги другим системам.
    link: integration
  - title: Независимость от поставщика
    description: >
      Избавьтесь от ограничений поставщика. С поддержкой 100+ поставщиков и постоянным расширением,
      получите истинно независимые от поставщика решения для гибкого управления сетью.
    link: vendor-agnostic
  - title: Проект с открытым исходным кодом
    description: >
      Воспользуйтесь преимуществами открытого исходного кода. NOC распространяется под лицензией BSD,
      способствуя сотрудничеству внутри активного и обширного сообщества.
    link: open-source
  - title: Микросервисная архитектура
    description: >
      Микросервисная архитектура с гибкими конвейерами обработки
      предоставляет большую гибкость, настройку и балансировку нагрузки.
    link: microservices
  - title: Webscale
    description: >
      Масштабируйтесь по мере роста. Начиная с простой установки на одном узле
      и заканчивая кластерами, управляющими крупнейшими сетями мира с миллионами объектов.
    link: webscale
  - title: Big Data
    description: >
      Внесите анализ Big Data в управление сетями. Встроенная база данных аналитики и предоставленные средства BI позволяют
    link: big-data
---
Добро пожаловать в NOC!

NOC - это масштабируемая, высокопроизводительная и система управления сетью с открытым исходным кодом для поставщиков интернет-услуг, сервисных и контент-поставщиков.

{{ show_highlights(page.meta.highlights) }}

## Структура Документации

Документация организована в четыре основных раздела:

- [Руководства](sections-overview/guides.md): Краткое введение для новых пользователей.
- [Справочник](sections-overview/references.md): Технический справочник.
- [Инструкции по использованию](sections-overview/howto.md): Пошаговые руководства, охватывающие общие проблемы.
- [Основы](sections-overview/background.md): Уточнение и обсуждение ключевых тем.

## Сообщество

Участие в сообществе NOC предоставляет вам прямой путь к установлению связей с другими опытными инженерами, разделяющими ваши интересы. Это возможность повысить осведомленность о захватывающей работе, которую вы выполняете, и совершенствовать свои навыки. Узнайте больше о том, как можно участвовать в нашем сообществе, обратившись к нашему [Руководству по сообществу](community-guide/index.md).

## Лицензия
NOC является программным обеспечением с открытым исходным кодом и распространяется на условиях [свободной open-source лицензии](license.md).
