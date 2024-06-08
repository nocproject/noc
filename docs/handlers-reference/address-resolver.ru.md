# Address Resolver

Интерфейс служит для определения (`resolve`) IP адреса устройства (`ManagedObject`) по полю `FQDN`.
Определение адреса запускается перед опросом и пытается определить IP адрес по DNS. Обработчик реализует собственный алгоритм определения IP адреса устройства.

Address Resolver применяется в начале опроса [Discovery](../discovery-reference/box/index.md).

 
    address_resolver(fqdn):
        Implements Address Resolver
    
        :param fqdn: Managed Object Instance FQDN field 
        :returns: 

## Примеры

### Определение адреса из локального файла 

При старте опроса проверяет локальный файл (должен находиться на одном хосте с процессом `Discovery`) и возвращает найденный IP адрес

```python
    import os

    FILENAME = "/tmp/device_addresses.txt"
    
    def address_resolver(fqdn):
        if os.path.exists(FILENAME):
            with open(FILENAME, "r") as f:
                for ll in f.readlines():
                    address, host = ll.split(",")
                    if fqdn.startswith(host):
                        return address

```
