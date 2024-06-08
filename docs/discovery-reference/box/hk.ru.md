# hk check

<!-- prettier-ignore -->
!!! todo
    Describe *hk* check

Позволяет проделать разнообразные операции по итогам прошедшего опроса. 
В конце опроса запускается обработчик [Handler](../../handlers-reference/index.md) с интерфейсом [Allow Housekeeper](../../handlers-reference/housekeeper.md). 
В него передаётся `Discovery check`, доступны любые методы из него.
 
## Требования

Необходимо активировать настройки в [Managed Object Profile вкладка Box](../../concepts/managed-object-profile/index.md#Box(Полный_опрос)):

* `Housekeeping` - включить `hk` check
* **Обработчик** (`handler`) - обработчик [Handler](../../handlers-reference/index.md)
