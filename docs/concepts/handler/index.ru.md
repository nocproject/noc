# Handler

<!-- prettier-ignore -->
!!! note
    Обработчики (`Handlers`) механизм расширения функционала требующий
    базовое знание `Python`

Один из механизмов расширения функционала `NOC` основан на обработчиках (`Handlers`). Это функции `Python`, 
которые позволяют изменить поведение системы там, где недостаточно обычных настроек. 
NOC предлагает множество мест, где пользовательски код может быть включён в механизмы системы, для 
организации собственного поведения. Подробный перечень всех возможных обработчиков и примеров к ним расположен в 
[Handlers Overview](../../handlers-reference/index.md).


## Соглашение по именованию

Обработчик (`Handler`), это указатель на функцию:

```
noc.custom.config.filters.MyFilter3
```

Префикс `noc` указывает, что обработчик ссылается на один из модулей NOCа. Использование иных префиксов 
позволяет обращаться к сторонним библиотекам или модулям. 
`MyFilter3` - функция (или другой допускающий вызов элемент) в модуле `noc.custom.config.filters`.

## Встроенные

Встроенные обработчики идут вместе с основным кодом NOC'a, например 
`noc.fm.handlers.event.link.oper_up` ссылается на функцию `oper_up` в файле:

```
<NOC root>
+-> fm
  +-> handlers
      +-> event
          +-> link.py
```

Встроенные обработчики используются в классах событий или аварий 

## Custom

Собственные (`Custom`) обработчики присоединяются к `noc` через репозиторий [Custom](../../custom/index.md) 
Собственные обработчики начинаются с префикса `noc.custom`. 
Например: `noc.custom.handlers.config.filters.MyFilter` ссылкается на функцию `MyFilter` из файла:

```
<NOC custom root>
+-> handlers
    +-> config
        +-> filters.py
```
<!-- prettier-ignore -->
!!! note
    Для их работы требуется подключенный `custom`

## PyRules

PyRules пользовательские модули Python хранимые в базе системы (`MongoDB`). Обращение к ним идёт через 
указатель, начинающийся с `noc.pyrules`, например: `noc.pyrules.config.filters.MyPyRuleFilter` 
ссылается на функцию `MyPyRuleFilter` из PyRule `config.filters`.


## Управление пользовательскими обработчиками

Для работы пользовательские обработчики (`Handler`)  необходимо зарегистрировать в системе. Это делается в 
меню `Основные (Main) -> Настройки (Setup) -> Обработчики (Handler)`.

* `Handler` - указатель на функцию (формат согласно соглашению о наименовании)
* Имя (`Name`) - имя обработчика (отображается при выборе)
* Описание (`Description`) - описание
* Поддерживаемые интерфейсы
    * `Config Handler`
        * `Allow Config Filter` - поддерживает фильтрацию конфигурации
        * `Allow Config Validation` - поддерживает валидацию конфигурации
        * `Allow Config Diff Filter` - поддерживает 
    * `Managed Object Profile Handler`
        * `Allow Housekeeping` - поддерживает `Housekeeper`
        * `Allow Resolver` - поддерживает механизм `Address Resolver` 
    * `Threshold Profile Handler`
        * `Allow Threshold` - 
        * `Allow Threshold Handler` - 
        * `Allow Threshold Value Handler` -  
    * `Other`
        * `Allow DS Filter` - 
        * `Allow IfDdesc` - 
        * `Allow MX Transmutation` - 
        * `Allow Match Rule` - 


