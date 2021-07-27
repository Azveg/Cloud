> Данная инструкци предполагает, что у вас:
>
> * есть учетная запись [Google Cloud Platform](https://cloud.google.com/)  
> * на локальном компьютере установлен [Python](https://www.python.org/downloads/) и [PyCharm](https://www.jetbrains.com/ru-ru/pycharm-edu/)
> * Вы знакомы с проектами [GoogEchoFunkBot](https://github.com/Azveg/Cloud_hub/tree/main/GoogEchoFunkBot) и [GoogTalkFunkBot](https://github.com/Azveg/Cloud_hub/tree/main/GoogTalkFunkBot)  

## GoogTalkFunkBotBQ  

Это развитие проекта [GoogTalkFunkBot](https://github.com/Azveg/Cloud_hub/tree/main/GoogTalkFunkBot).  

Следующим шагом развития стало:  
* подключение бота к DWH Google Big Query 
* использовались дополнительные библиотеки (google, pandas_gbq)


### Начало работы с Big Qouery  

Самое лучшее описание того как создать первый датасет, таблицу и загрузить туда данные находится здесь --> [Quickstart using the Cloud Console](https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui?_ga=2.240089027.-1156589723.1624522742%D0%99)  

Когда датасет и таблица созданы, данные туда успешно загружены пусть пока из файла, то нам необходимо скачать ключ доступа для работы с Big Query через pandas это делается следующим образом:  
> * заходим в проект  
> * IAM & Admin  
> * Service accounts  
> * Action  
> * Manage keys  
> * ADD KEY  
> * Create new key  
> * JSON  
> * Create   
> * скачиваем ключ  

Теперь с помощью ключа и библиотеки pandas_gbq мы можем работать с DWH Big Query из нашего кода.  

### Дополняем проект в PyCharm  

1. Дополняем файл requirements.txt, измененный файл должен выглядить так:  
```
python-telegram-bot==13.4.1
pandas
pyarrow
sklearn
google
pandas_gbq
```

2. Загружаем данные в Big Query  
В предыдущем проекте в качестве источника данных использовался файл `df.parquet` теперь необходимо его загрузить в хранилище.  
Для этого пользуясь инструкцией [Quickstart using the Cloud Console](https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui?_ga=2.240089027.-1156589723.1624522742%D0%99) создаем таблицу с типом Upload и задаем следующие поля:  
`context_2, context_1, context_0, reply, label`


3. Создаем файл big_query.py и вставляем туда следующий код:
```python
from google.oauth2 import service_account
import pandas_gbq

# копируем ID проекта и записываем в переменную  
project_id = 'my_project_id'
# указываем путь к скачанному файлу ключа  
credentials = service_account.Credentials.from_service_account_file('credentials.json')
# указываем таблицу в формате ID проекта-имя датасета-имя таблицы   
table_from = 'my_project_id.my_data_set.my_table'

pandas_gbq.context.credentials = credentials
pandas_gbq.context.project = project_id


def select_big_query():
    # с помощью библиотеки pandas_gbq формирует DataFrame из запроса к таблице в Big Query
    return pandas_gbq.read_gbq(f"SELECT context_0, reply FROM `{table_from}`")
```

4. Правим файл panda.py в части ссылок на данные, полный текст файла ниже:
```python
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import BallTree
from sklearn.base import BaseEstimator
from sklearn.pipeline import make_pipeline
import numpy as np
import re
import big_query

# импортируем DataFrame из файла big_query.py  
dd = big_query.select_big_query()
# Векторизация текстов
# ----------------------------------------------------
# создаем объект, который будет преобразовывать короткие тексты в числовые векторы
vectorized = TfidfVectorizer()
# обучаем его на всех контекстах -> запоминаем частоту каждого слова
# записываем в матрицу, сколько раз каждое слово встречалось в тексте
matrix_big = vectorized.fit_transform(dd.context_0)

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
ns.fit(matrix_small, dd.reply)
pipe = make_pipeline(vectorized, svd, ns)


def answer(question):
    return re.sub('[^А-я,?!.\\s]', '', str(pipe.predict([question])))
```

5. Проводим деплой аналогично предыдущему проекту:  

Функция деплоя программы:  

`gcloud functions deploy telegram_bot --set-env-vars "TELEGRAM_TOKEN=<TELEGRAM_TOKEN>" --runtime python38 --trigger-http --project=<project_name> ` 

Функция повторного деплоя программы:  

`gcloud functions deploy telegram_bot --runtime python38 --trigger-http --project=<project_name>`  

Функция проверки деплоя программы:  

`curl "https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook?url=<URL>"`  


6. Результат  

В этот раз ответы бота были достаточно сумбурные:  
```
Антон: Привет
GoogTalkFunk: привет , ник .
Антон: как дел?
GoogTalkFunk: она в порядке .
Антон: кто она то?
GoogTalkFunk: долбаная дверь .
Антон: что с ней?
GoogTalkFunk: ты говорил с ней .
Антон: я что дурак по твоему?
GoogTalkFunk: мне нравится эта часть .
Антон: пошел ты...
Антон: ?
Антон: не знаешь что сказать?
GoogTalkFunk: ни в коем случае . я не забыл ! как е забудешь !
GoogTalkFunk: отвечай !
GoogTalkFunk: подчинись и будешь вознаграждена .
```
