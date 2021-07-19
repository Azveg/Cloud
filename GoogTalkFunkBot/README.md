> Данная инструкци предполагает, что у вас:
>
> * есть учетная запись [Google Cloud Platform](https://cloud.google.com/)  
> * на локальном компьютере установлен [Python](https://www.python.org/downloads/) и [PyCharm](https://www.jetbrains.com/ru-ru/pycharm-edu/)
> * Вы знакомы с проектом [GoogEchoFunkBot](https://github.com/Azveg/Cloud_hub/tree/main/GoogEchoFunkBot) 



### GoogTalkFunkBot

Это развитие проекта [GoogEchoFunkBot](https://github.com/Azveg/Cloud_hub/tree/main/GoogEchoFunkBot), в отличии от Эхо-бота, нынешний бот старается отвечать осмысленно.   
Следующим шагом в развитии бота стало:  
* усложнение структуры (добавился файл с данными и второй файл с python скриптом)
* использовались дополнительные библиотеки (re, pandas, sklearn)
* производятся математические вычисления для обработки ответов (идея и код реализации обработчика взят из статьи [Создание простого разговорного чатбота в python](https://habr.com/ru/post/462333/)  


> Следующие шаги аналогичны проекту Эхо-бота:
> 
> * Создание проекта Google Cloud Platform  
> * Регистрация телеграм бота
> * Установка Google Cloud SDK
> * Файл с контекстами и ответами лежит в исходниках, файл от Яндекса приманяемый для обучения Алисы, переведен в формат parquet для экономии места на диске
> * Создание проекта в PyCharm, кроме шага 5 (создание файла requirements.txt)  
> Что такое requirements.txt и как с ним работать можно прочесть [здесь](https://t.me/best_practices_it/107)




### Дополняем проект в PyCharm  

1. Дополняем файл requirements.txt, измененный файл должен выглядить так:  
  
```
python-telegram-bot==13.4.1
pandas
pyarrow
sklearn
```

2. Создаем файл panda.py и вставляем туда следующий код:    

```python
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import BallTree
from sklearn.base import BaseEstimator
from sklearn.pipeline import make_pipeline
import numpy as np
import re


df = pd.read_parquet('df.parquet')

# Векторизация текстов
# ----------------------------------------------------
# создаем объект, который будет преобразовывать короткие тексты в числовые векторы
vectorized = TfidfVectorizer()
# обучаем его на всех контекстах -> запоминаем частоту каждого слова
vectorized.fit(df.context_0)
# записываем в матрицу, сколько раз каждое слово встречалось в тексте
matrix_big = vectorized.transform(df.context_0)

# Сокращение размерности
# ------------------------------------------------
# алгоритм будет проецировать данные на 300-мерное пространство
svd = TruncatedSVD(n_components=300)
# коэф. этого преобразования выучиваются так, чтобы сохранить максимум информации об исходной матрице
svd.fit(matrix_big)
matrix_small = svd.transform(matrix_big)


# Поиск ближайших соседей
# ---------------------------------------
def softmax(x):
    proba = np.exp(-x)
    return proba / sum(proba)


class NeighborSampler(BaseEstimator):
    def __init__(self, k=5, temperature=1.0):
        self.k = k
        self.temperature = temperature

    def fit(self, X, y):
        self.tree_ = BallTree(X)
        self.y_ = np.array(y)

    def predict(self, X, random_state=None):
        distances, indices = self.tree_.query(X, return_distance=True, k=self.k)
        result = []
        for distance, index in zip(distances, indices):
            result.append(np.random.choice(index, p=softmax(distance * self.temperature)))
            return self.y_[result]


# соединяем методы векторизации, сокращения размерности и поиска соседей
ns = NeighborSampler()
ns.fit(matrix_small, df.reply)
pipe = make_pipeline(vectorized, svd, ns)


def answer(question):
    return re.sub('[^А-я,?!.\\s]', '', str(pipe.predict([question])))

```


3. Обновляем файл main.py

нам нужно добавить импорт из файла panda.py и изменить строку с отправкой ответного сообщения  

```python
import os
import telegram
import panda


def talk_bot(request):
    # определяем бота с помощью токена
    bot = telegram.Bot(token=os.environ["TELEGRAM_TOKEN"])
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        chat_id = update.message.chat.id
        # вызываем метод panda.answer для формирования ответного сообщения
        bot.sendMessage(chat_id=chat_id, text=panda.answer(str(update.message.text)))
    return "okay"
```

4. Производим разворачивание функции аналогично проекту Эхо-бота

> При возникновении ошибки: "Error: memory limit exceeded. Function cannot be initialized."
> 
> Необходимо увеличить выделяемую память на функцию: 
> заходим в функцию --> EDIT -->  Runtime, build and connections settings --> Memory allocated (у меня функция развернулась при 1 Гб)  

5. Проверяем бота

У меня получилось что-то такое:

```
Антон: Привет
GoogTalkFunk: привет
Антон: как дела?
GoogTalkFunk: лучше некуда .
Антон: чем занимаешься?
GoogTalkFunk: мы пьем .
Антон: почему меня не позвали?
GoogTalkFunk: потому что я хочу знать , сколько денег вы зарабатываете .
Антон: это не твоё дело!
GoogTalkFunk: очень даже мое .
Антон: Ты моя жена?
GoogTalkFunk: жена ?
Антон: Да, жена
GoogTalkFunk: я видел это только на картинках .
```
