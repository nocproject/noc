# Event Classification Rule

Предназначены для определения класса событий, поступающих с оборудования.

## Настройки

Настройки правил классификации событий расположены в 
`Управление авариями (Fault Management) -> Настройки (Setup) -> Правила классификации (Classification Rule)`

* **Имя** (`Name`) - название правила. Используется нотация с разделением по категориям
* **Описание** (`Description`) - описание правила
* **Приоритет** (`Priority`) - приоритет проверки правила
* **Класс события** (`Event Class`) - выставляется при совпадении
* **Шаблоны** (`Patterns`) - список шаблонов, проверяемых на совпадение с событием
    * `RE Key` - регулярное выражение для названия переменной
    * `RE Value` - регулярное выражение для значения переменной
* **Переменные** (`Vars`) - добавляет указанные переменные в событие
   * Имя (`Name`) - имя переменной
   * Значение (`Value`) - значение

## Описание работы

Правила применяются классификатором в порядке возрастания приоритета (`Preference`) до полного совпадения регулярных 
выражений, перечисленных в шаблонах (`Patterns`). При полном совпадении событию назначается класс события из настроек, 
а именованные группы из регулярных выражений становятся переменными, имя группы - имя переменной, совпадение - это значение переменной.


## Пример

