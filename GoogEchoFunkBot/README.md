> Данная инструкци предполагает, что у вас:
>
> * есть учетная запись [Google Cloud Platform](https://cloud.google.com/)  
> * на локальном компьютере установлен [Python](https://www.python.org/downloads/) и [PyCharm](https://www.jetbrains.com/ru-ru/pycharm-edu/)

### Создание проекта Google Cloud Platform  

1. В верхней панели выбираем `Select a project` --> `New project`  
2. заполняем поле `Project name`
3. нажав на многоточие в правом углу меню можно, выбрав `Project settings`, перейти на страницу описание проекта и в том чиле узнать `Project ID`


### Регистрация телеграм бота

1. находим в телеграме `@BotFather`
2. вводим `/newbot`
3. вводим имя бота
4. повторно вводим имя бота с окончанием `…bot`  
  4.1 в ответ придет ссылка на бот и токен для доступа к нему, сохраняем ссылку и токен с отдельный текстовый файл


### Установка Google Cloud SDK

1. Выполняем установку Cloud SDK, это нужно для разворачивания фунций в облако с локального компьютера.
2. Переходим на страницу [Installing Google Cloud SDK](https://cloud.google.com/sdk/docs/install)  
3. скачиваем дистрибутив для своей операционной системы и следуем инструкции по установке
4. если консоль не запустилась автоматически, то  
  4.1 запускаем ***Google Cloud SDK Shell***  
  4.2 выполняем `gcloud init`  
  4.3 следуем подсказакам консоли и выполняем настройку подключения к проекту  
  

### Создание проекта в PyCharm

1. создаем проект со стандартными настройками  
2. создаем python файл с именем main и вставляем следующий код

```python
import os
import telegram

def telegram_bot(request):
# определяем бота методом telegram.Bot по его токену
    bot = telegram.Bot(token=os.environ["TELEGRAM_TOKEN"])
    # если метод у пришедшего запроса POST, то
    if request.method == "POST":
        # пришедший в формате JSON запрос ассоциируем с нашим ботов и переводим в Telegram object 
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        # из телеграм объекта получаем идентификатор чата
        chat_id = update.message.chat.id
        # отправляем ответное сообщение по идентификатору чата
        bot.sendMessage(chat_id=chat_id, text=update.message.text)
    return "okay"
```

3. создаем .gitignore file   
  3.1 в настройках PyCharm находим плагин .ignore и устанавливаем  
  3.2 вызываем контекстное меню на корневой папке проекта и выбираем:   
`new → .ignore File → .gitignore File (Git) → в languages, frameworks выбираем Python и JetBrains → generate`  
  3.3 Для создание файла gitignore для Google Cloud выбираем:   
  `new → .ignore File → .gcloudignore File (Google Cloud) → generate`
    3.3.1 открываем файл и вставляем следующий код  
    
    ```
    # This file specifies files that are *not* uploaded to Google Cloud Platform
    # using gcloud. It follows the same syntax as .gitignore, with the addition of
    # "#!include" directives (which insert the entries of the given .gitignore-style
    # file at that point).
    #
    # For more information, run:
    #   $ gcloud topic gcloudignore
    #
      .gcloudignore
    # If you would like to upload your .git directory, .gitignore file or files
    # from your .gitignore file, remove the corresponding line
    # below:
      .git
      .gitignore
      README.md
    #!include:.gitignore
    ```
  
  4. Создаем файл README.md и вставляем следующий код:  

```
create a Google Cloud Function running this command in the same line:

gcloud functions deploy telegram_bot --set-env-vars "TELEGRAM_TOKEN=<TELEGRAM_TOKEN>" --runtime python38 --trigger-http --project=<project_name>

you can also specify the region by appending the following string to the previous command

--region=<region_name>
list of the available regions

Some details:

Here webhook is the name of the function in the main.py file
You need to specify your Telegram token with the --set-env-vars option
--runtime python38 describe the environment used by our function, Python 3.8 in this case
--trigger-http is the type of trigger associated to this function, you can find here the complete list of triggers The above command will return something like this:
Step three, you need to set up your Webhook URL using this API call:

curl "https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook?url=<URL>"

```

5. создаем файл requirements.txt и прописывем туда:  

```
python-telegram-bot==13.4.1
```
  5.1 PyCharm предложит установить зависимость, выполняем  
  

### Создание функции с ботом в облаке  

1. открываем терминал в PyCharm или терминал Google Cloud SDK Shell  
  1.1 если в PyCharm не проходят команды gcloud, то выполняем их в Google Cloud SDK Shell, поменяв директорию по умолчанию на директорию проекта через команду:   
```
cd C:\repos\cloud\GoogEchoFunkBot
```

2. заходим в файл README.md, копируем строку  

```
gcloud functions deploy telegram_bot --set-env-vars "TELEGRAM_TOKEN=<TELEGRAM_TOKEN>" --runtime python38 --trigger-http --project=<project_name>

```
3. меняем часть строки `<TELEGRAM_TOKEN>` на токен полученный в разделе регистрации бота и `<project_name>` на id проекта, который можно скопировать из консоли Google Cloud  
4. вставляем измененную строку в терминал и выполняем  
5. если все правильно сделано появится вопрос: _Allow unauthenticated invocations of new function [telegram_bot]_?  
  5.1 отвечаем _Да_
6. Начнется деплой функции в облако  
7. После успешного деплоя копируем строку с URL  
8. Можно просто перейти по ссылке из п. 7, должен произойти переход на страницу с текстом “okay“  
9. Далее для проверки работы функции копируем из README строку и вставляем туда токен и ссылку из пункта 7  

```
curl "https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook?url=<URL>"
```

10. Вставляем в терминал строку из п. 9 и выполняем должна вернуться строка   

```
{"ok":true,"result":true,"description":"Webhook is already set"}
```


### Повторный деплой функции  

После внесения изменений в программу необходимо повторно задеплоить функцию в облако. Это делается аналогично первичному деплою, только строку необходимо изменить на  

```
gcloud functions deploy telegram_bot --runtime python38 --trigger-http --project=<project_name>
```

так как переменные среды уже создавать не нужно.

---

Инструкция сделана на основе материалов видео [Build, deploy and host a Telegram Bot on Google Cloud Functions for free using Python](https://www.youtube.com/watch?v=jzwMzUAAOWk&lc=z23bc3byuzvps1o5s04t1aokgqdpxagnb3etfxqoziqzbk0h00410.1626244286668840) на канале [Federico Tartarini](https://www.youtube.com/channel/UCRjhrVMfeAurqHm4BnTNgyw)
