# BFD 

`Bidirectional Forwarding Detection` применяется для отслеживания за ошибками связи путём установки сессии между двумя
 `forwarding_engine`. По этой сессии возможно построение линка между устройствами.


## Требования

* Скрипт [get_bfd_sessions](../../scripts-reference/get_bfd_sessions.md)
* Возможность [Network BFD](../../caps-reference/network.md#network-bfd)
* Опрос BFD включён в профиле объектов [Managed Object Profile](../../concepts/managed-object-profile/index.md#Box(Полный_опрос))
* Метод BFD в *Методах построения топологии* [Segment Profile](../../concepts/network-segment-profile/index.md)
