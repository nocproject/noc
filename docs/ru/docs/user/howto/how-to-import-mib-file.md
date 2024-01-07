# Как импортировать MIB файл в НОК

## Описание

**MIB** - файлы содержащие инфофрмацию для резолва бинарное информации (SNMP OID) в читаемый формат. В НОКЕ они применяются для:

1. Преобразования числовых представлений OIDов из трапов `SNMPTrap`, в текстовые 
2. В скриптах `SA` для удобства использования текстовых наименований и подсказок по преобразованию значений.

!!! attention
    Для импорта `MIB` используются утилиты `smidump` и `smilint`, поэтому необходимо наличие всех зависимых **MIB файлов**

## Требования

1. Установить в систему утилиты для работы с MIB файлами: `smidump` и `smilint` (ставится с пакетом `netsnmp-utils`)
2. Набор необходимых `MIB` файлов. Вместе с пакетом `netsnmp-utils` 
   идут стандартные мибы, распологаются в  `/usr/share/mibs/ietf/`.
3. Если планируется испорт из `WEB` интерфейса - необходимо установить сервис `MIB` (через башню)

### Подготовка инфраструктуры

Для успешного импорта необходимо подготовить инфраструктуру:

> В случае многонодовой инсталляции действия выше необходимо провести на ноде с сервисом `MIB`


1. Проверяем доступность утилит `smidump` и `smidump`:

```
# smidump --v
smidump 0.4.8
# smilint --v
smilint 0.4.8
```

2. В файл `etc/settins.yml` (если нет - необходимо создать) прописываем 
   пути до утилит `smidump` и `smidump` и путь к директории с мибами:

```

path:
  mib_path: /usr/share/mibs/ietf/:/usr/share/mibs/site/:/opt/noc/var/mibs/dist/
  smilint: /usr/bin/smilint
  smidump: /usr/bin/smidump

```

3. В случае вашей системы пути могут отличаться
4. Складываем необходимые для импорта файлы с зависимостями в папку из `mib_path`,
   например `/usr/share/mibs/site/`
5. Устанавливаем MIB файлы для НОКа: `./scripts/deploy/install-packages requirements/mib.json`

### Импорт MIB файла

!!! attention
    Для импорта `MIB` используются утилиты `smidump` и `smilint`, поэтому необходимо наличие всех зависимых **MIB файлов**

Импортировать MIB файл возможно двумя путями:

* Через WEB-интерфейсе `Fault Management -> MIB` (требует сервис `MIB`)
* При помощи команды `./noc mib --local import` (ключ `--local` говорит не использовать сервис `MIB`)

**WEB**

!!! attention
    Для работы через `Web` необходим установленный сервис `MIB`.

1. Переходим в меню `Fault Management (Управление авариями) -> MIB`
2. Нажимаем кнопку **Добавить** (`Add`)
3. Заполняем форму МИБ файлом и зависимостями (если необходимы).
4. Нажимаем Загрузить (`Upload`)

**Команда**

1. Выполняем команду для импорта `./noc mib --local import <MIBFILE>`, где `<MIBFILE>` путь к файлу `MIB`, либо директории с файлами.
2. Если в конце вывода написано `Pass MIB through smilint to detect missed modules` с перечнем недостающих файлов,
 необходимо разместить их в одной из указанных в `mib_path` директорий и повторить команду.
3. Если файлы не указаны, значит импорт прошёл успешно. Проверить можно в веб интерфейсе `Fault Management -> MIBs`

### После

После успешного импорта `MIB` необходимо перезапустить **классификатор**.