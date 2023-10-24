# Инвентаризация

Мы абсолютно уверены, что мониторинг без базовой инвентаризации - это профанация. Вам необходимо знать, что у вас есть, а затем проверить его на работоспособность. Централизованная база данных ваших активов, обычно называемая **Сетевым Ресурсным Инвентарем** (*Network Resource Inventory*, NRI) или просто **Инвентарем** (*Inventory*).

NOC сосредотачивает вас на поддержании актуальной и чистой инвентаризации и определении политик мониторинга. Политики представляют собой групповые настройки, которые применяются автоматически, когда выполняются все предварительные условия. Таким образом, поддерживая инвентаризацию, вы получаете мониторинг как бонус.

NOC поддерживает как физическую, так и логическую инвентаризацию.

Физическая инвентаризация включает в себя:

* Точки присутствия (PoP) с географическими координатами.
* Этажи, комнаты, стойки.
* Кабельную инфраструктуру (колодцы и кабельные каналы).
* Шасси, линейные карты, оптические модули.
* Физические интерфейсы.

Логическая инвентаризация включает в себя:

* Управляемые объекты.
* Логические интерфейсы (субинтерфейсы).
* L2-связи.
* Сетевые сегменты.
* Проекты.
* Поставщики.
* Абоненты и услуги.
* VPN, IP-префиксы, IP-адреса (IPAM).
* VLANы.
* Планы набора номеров, диапазоны номеров и телефонные номера.
* Сеансы проверки SLA.
* Автономные системы (AS) и BGP-пиры.
* MAC-адреса.

NOC автоматически заполняет большую часть данных инвентаризации с помощью [процесса обнаружения](../discovery-reference/index.md).

## См. также

* [Функции обработки топологии](../topology-processing-features/index.md)
* [Справочник по обнаружению](../discovery-reference/index.md)