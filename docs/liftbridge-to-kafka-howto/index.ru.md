# Как заменить Liftbridge на Kafka


С какого-то момента сервис Liftbridge стал плохо себя вести под нагрузкой, а также был заброшен как проект, поэтому мы решили переключить основную очередь на Kafka.


## Tower настройки:

1. Снять галочки с `liftbridge` и `nats` сервисов, они больше не потребуются. 

2. Решите, сколько узлов kafka будет в вашем кластере. Возможное количество: 1, 3, 5. 1 — минимальный кластер.

3. Поставьте галочки на сервисы `kafka` на нужных нодах. Заполните `Kafka Cluster Id`, если хотите, и убедитесь, что он одинаков на каждой ноде. Заполните лимит памяти JVM, 1 ГБ будет достаточно для небольшой установки.

4. Убедитесь, что вы используете `consul` для управления настройками (это когда у вас есть "consul://consul/noc" в `Config Load Preference Path` на главной странице `ENV` в `Tower`), в противном случае вам необходимо добавить настройки в локальный файл конфигурации в `/opt/noc/etc/settings.yml`:

```
redpanda:
  addresses: kafka
msgstream:
  client_class: noc.core.msgstream.redpanda.RedPandaClient
```

5. Деплой

6. После успешного деплоя можно удалить старые сервисы из системы

```
systemctl stop liftbridge
systemctl stop nats-server
systemctl disable liftbridge
systemctl disable nats-server
rm -rf /var/lib/liftbridge/*
```
