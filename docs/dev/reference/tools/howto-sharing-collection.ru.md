---
tags:
  - how-to
---
# Как Добавить коллекцию в общий доступ из Пользовательского интерфейса НОКа

НОК это проект с открытым исходным кодом, поэтому любой может поучаствовать в его развитии.
Коллекции настроек важная часть НОКа, они предоставляют простой путь добавления ваших
наработок (моделей оборудования, профилей, моделей) для использования всех пользователей.

Consider you have got a self-made collection, for example a new model of switch or connection rule or etc.
Follow the steps:

1. Зарегистрировать в нашем трекере [Gitlab](https://code.getnoc.com/)
2. Создать [Персональный токен доступа - Personal Access Token](https://code.getnoc.com/profile/personal_access_tokens>) с отмеченной областью `api`.
   Сохраните его!
3. Откройте модель, которую вы хотите добавить в проект в Веб-интерфейсе, например:
   ![JSON](image/json.png)
4. Заполнител предложенные формы.
   ![JSON2](image/json2.png)
   ![API Key](image/apikey.png)
   ![Description](image/description.png)
5. НОК отправит файл (у браузера должен быть доступ в интернет) в репозиторий и откроет `Merge Request` (запрос на добавление).
   Некоторые браузеры откроют окно с предупреждением, проверьте этот момент.
   ![MR](image/mr.png)
6. Подзравляем! Вы добавили ваш труд в проект. Спасибо!

## Изменение или Восстановление токена доступа
Если вы забыли ваш токен для доступа или хотите его поменять:

```
$ ./noc shell
from noc.core.mongo.connection import connect
connect()
from noc.main.models.apitoken import APIToken
from noc.aaa.models.user import User
user = User.objects.get(username="YOUR_NOC_LOGIN")
token = APIToken.objects.filter(type="noc-gitlab-api", user=user.id).first()
token.token = "NEW_TOKEN"
token.save()
```