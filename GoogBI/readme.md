# GoogBI

# Содержание

1. Описание проекта
2. архитектура
3. часть отвечающая за тинькоф и big query
4. дашборд
5. мини отчет в телеграм
6. бот телеграм и планировщик
7. создание канала и получение его ID
8. создание бота
9. настройка запуска по расписанию
10. итоги
11. Релизы
12. Литература и ссылки




# Описание проекта  

 > Добработать описание  
>> ### Должно быть полноценным описанием продукта (поискать хорошие примеры)  
 > включить эскизы дашборда и мини отчета
  
Данный проект создан для анализа инвестиций через брокера Тинькофф.  
Его суть - получать аналитику по портфелям в автоматизированном режиме в нескольких форматах.  
Аналитика в виде дашборда (отчет с графиками) и мини-отчет с ключевыми показателями. Дашборд отправляется еженедельно на почту, а мини-отчет в телеграмм.   

> Проект также будет развиваться и функциональность описанная ниже дополнится новыми возможностями, а отчетность новыми показателями.  

# Архитектура
  
![GoogBI](/GoogBI/.idea/Screenshot_1.png "Схема архитектуры")

> Изначально все процессы ETL по загрузке, преобразованию и записи данных планировалось сделать на основе Google Cloud Function, однако оказалось, что все три, рекомендованные библиотеки Python для взаимодействия с API Тинькофф, не добавлены в общий индекс библиотек и поэтому при деплое функции в облака падает ошибка.  

Поэтому на данном этапе первоночальная загрузка проводится ручным запуском кода из IDE PyCharm. 

## Описание компонентов  
1. PyCharm
2. Тинькоф API
3. Big Query
4. Google Data Studio
5. Google Cloud Scheduller
6. Google Cloud Function
7. Телеграм


## Этапы работы программы:
1. из PyCharm отправляем запрос к Тинькоф на получение данных по портфелю, соверщенным сделкам и инструментам, которые торгует брокер
2. Тинькоф API возвращает результаты
3. Пишем полученные данные в таблицы Big Query
4. К созданным таблицам интегрируемся из Google Data Studio через встроенные коннекторы
5. Google Cloud Scheduller по расписанию запускает Cloud Function
6. Cloud Function обращается к Big Query
7. Cloud Function получает данные из Big Query и преобразует в нужный вид
8. Cloud Function отправляет отчет в телеграм канал через телеграм бота

# Обработка инвестиционных данных

## Подготовительный этап

### Получение токена Тинькофф инвестиций  

> 1. Получаем токен для взаимодействия с Тинькоф API    
> Подробная инструкция приведена на сайте [Тинькоф инвестиций](https://tinkoffcreditsystems.github.io/invest-openapi/auth/)  

---

### Создание аккаунта Google Cloud  

Создание аккаунта на платформе Google интуитивно понятно, здесь мы не будем углубляться в эту тему, оставлю пару полезных видео, которые помогут разобраться с основами:  

- [Welcome to Google Cloud Platform - the Essentials of GCP](https://www.youtube.com/watch?v=4D3X6Xl5c_Y)
- [Creating a billing account](youtube.com/watch?v=NeRYUoR4u0s)
- [Managing billing permissions](https://www.youtube.com/watch?v=TDHTcS2V4wI)
- [Closing your billing account](https://www.youtube.com/watch?v=_elELrPReWU)
- [The Google Cloud Platform Free Trial and Free Tier](https://www.youtube.com/watch?v=P2ADJdk5mYo)
- [Creating, managing, and retiring Service Accounts](https://www.youtube.com/watch?v=2TdLmI3G5Rc)
---

### Создание проекта в Google Cloud 

После регистрации необходимо создать проект, делаем это следующим образом:  
> 1. В верхней панели выбираем `Select a project` --> `New project`  
> 2. заполняем поле `Project name`
> 3. нажав на многоточие в правом углу меню можно, выбрав `Project settings`, перейти на страницу описание проекта и в том чиле узнать `Project ID`
---

### Получение ключа доступа к Google Cloud

Когда проект создан, то нам необходимо скачать ключ доступа для работы с Big Query через pandas_gbq это делается следующим образом:  
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

---

### Создание таблиц в Big Query

Создаем дасет и таблицы, инструкция и описание начала работы с Big Query приведена здесь: [Quickstart using the Cloud Console](https://cloud.google.com/bigquery/docs/quickstarts/quickstart-cloud-console?_ga=2.240089027.-1156589723.1624522742%D0%99)   
В отличии от инструкции, можно создать поля в таблице через кнопку "Add field" сразу указывая тип данных. 

Нам понадобится создать 4 таблицы:  

- deal - таблица сделок и операций, в ней отражены все покупки и продажи, зачисление дивидендов и купонов, в общем все события по счету

| Field name      | Type Mode | Description                               |
| :-------------: |:---------:| :--------------------------------------:  |
| figi	          |STRING	    |идентификатор инструмента	                |
| date	          |STRING	    |дата сделки	                              |
| instrument_type	|STRING	    |тип инструмента (акция, облигация и т.д.)	|
| currency	      |STRING	    |валюта, в которой торгуется инструмент	    |
| operation_type	|STRING	    |тип операции (покупка, продажа и т.д.)	    |
| payment	        |FLOAT	    |сумма сделки	                              |
| price	          |STRING	    |цена актива (нпр. цена за 1 лот)	          |
| quantity	      |STRING	    |количество активов в сделке	              |
| commission	    |STRING	    |коммиссия по операции	                    |
| portfolio	      |STRING	    |портфель к которому относится сделка       |


- instruments - таблица справочник, всех инструментов, торгуемых брокером Тинькоф

| Field name          | Type Mode | Description                                                     |
| :-----------------: |:---------:| :--------------------------------------------------------------:|
| currency	          |STRING	    |	валюта, в которой торгуется инструмент                          |
| figi	              |STRING	    | идентификатор инструмента	                                      |
| isin	              |STRING	    | Международный идентификационный код ценной бумаги	              |
| lot	                |STRING	    | количество ценных бумаг в 1 лоте                                |
| min_price_increment	|STRING	    | шаг цены инструмента	                                          |
| name	              |STRING	    | Наименование инструмента                                        |
| ticker	            |STRING	    | краткое название в биржевой информации котируемых инструментов.	|
| type	              |STRING	    | тип инструмента (акция, облигация и т.д.)	                      |


- portfolio - таблица в которой хранятся все активы по портфелям и данные о них

|Field name       | Type      | Description|
| :-------------: |:---------:| :------------------------------------------------------------------------------------------------------------------:|
|figi	            |STRING	    |идентификатор инструмента		                                                                                        |
|name	            |STRING	    |Наименование инструмента	                                                                                            |
|ticker	          |STRING	    |краткое название в биржевой информации котируемых инструментов.	                                                    |
|currency	        |STRING	    |валюта, в которой торгуется инструмент 	                                                                            |
|balance	        |FLOAT	    |количество в портфеле	                                                                                              |
|income	          |FLOAT	    |прибль/убыток от изменения цены 	                                                                                    |
|price	          |FLOAT	    |цены покупки	                                                                                                        |
|portfolio	      |STRING	    |портфель к которому относится инструмент	                                                                            |
|instrument_type	|STRING	    |тип инструмента (акция, облигация и т.д.)	                                                                          |
|position	        |FLOAT	    |сумма по инструменту в рублях (price * курс к рубль на день сделки * balance + income * курс к рублю на текущий день	|


- portfolio_value - таблица хранящая срез по ценам активов на дату. Нужна для отслеживания динамики стоимости портфеля.

| Field name      | Type      | Description|
| :-------------: |:---------:| :--------------------------------------:  |
| portfolio	      | STRING	  | портфель к которому относится инструмент	|
| instrument_type	| STRING	  | тип инструмента (акция, облигация и т.д.)	|
| position	      | FLOAT	    | сумма по активу в рублях	                |
| date	          | STRING	  | дата записи данных	                      |
 

---

## Проект в PyCharm

- Создаем проект в IDE PyCharm, здесь будем писать код на языке Python для выгрузки, обработки и записи инвест данных.  

### 1. создаем проект со стандартными настройками  
> как создать проект да ещё со стандартными настройками????? 

---

### 2. Создаем файл requirements.txt и вставляем следующий код:


```text
google
pandas_gbq
pycbrf
tinkoff-invest-openapi-client==0.0.7
```

> это файл описывающий зависимости, т.е. те сторонние библиотеки, которые будем использовать в проекте.  
> Такое описание необходимо при развертывании кода в облаке, чтобы нужные библиотеки функционировали.

---

### 3. создем python файл с именем auth и вставляем следующий код:  


```python
from openapi_client import openapi
from google.oauth2 import service_account
import pandas_gbq

# авторизация в тинькофф инвестициях
# авторизация в тинькофф инвестициях
token = 'токен тинькоф'

client = openapi.api_client(token)
broker_account_id_iis = 'ID счета ИИС'
broker_account_id_tf = 'ID основного счета'

# авторизация в google cloud
project_id = 'ID проекта в Google Cloud'

credentials = service_account.Credentials.from_service_account_file('ключ доступа к Google Cloud.json')
pandas_gbq.context.credentials = credentials
pandas_gbq.context.project = project_id

# получение счетов в Тинькофф брокере
# Для дальнейшей работы необходимо получить идентификаторы портфелей, 
# это нужно если у вас несколько портфелей и вы хотите делать раздельную аналитику по ним.
s = openapi.api_client(token).user.user_accounts_get()
print(s)
# {'broker_account_id': 'ID счета','broker_account_type': 'Tinkoff'},
# {'broker_account_id': 'ID счета','broker_account_type': 'TinkoffIis'}
# Получившиеся результаты вставляем в значения переменных broker_account_id_tf и broker_account_id_iis
```
> В файле auth приведен код авторизации в Google Cloud и  Тинькоф, а также получение идентификаторов счетов Тинькоф

---

### 4. создаем python файл с именем main и вставляем следующий код  


```python
from portfolio import portfolio_write, portfolio_value_write
from deal import deal_write
from instruments import instrument_write


portfolio_write()
deal_write()
instrument_write()
portfolio_value_write()
```

> В файле Main будут вызовы функций записи в таблицы, которые создали выше. 

### 5. создем python файл с именем portfolio и вставляем следующий код:  


```python
import pandas as pd
import numpy as np
from auth import client, broker_account_id_iis, broker_account_id_tf, project_id
import pandas_gbq
from pycbrf.toolbox import ExchangeRates
from datetime import datetime
from pytz import timezone

iis = client.portfolio.portfolio_get(broker_account_id=broker_account_id_iis)
tf = client.portfolio.portfolio_get(broker_account_id=broker_account_id_tf)
iis_rub = client.portfolio.portfolio_currencies_get(broker_account_id=broker_account_id_iis)
tf_rub = client.portfolio.portfolio_currencies_get(broker_account_id=broker_account_id_tf)
x = 0
table_name = 'invest.portfolio'
# получаем текущий день
today = datetime.now(tz=timezone('Europe/Moscow'))
# запрашиваем курсы валют через ЦБ
curs = ExchangeRates(str(today.date()))
usd = float(curs['USD'].value)
eur = float(curs['EUR'].value)

df = pd.DataFrame(columns=['figi', 'name', 'ticker', 'currency', 'balance', 'income', 'price', 'portfolio', 'instrument_type'])

# ИИС
for i in iis.payload.positions:
    df.loc[x] = [i.figi, i.name, i.ticker, i.average_position_price.currency, i.balance, i.expected_yield.value, i.average_position_price.value, 'IIS', i.instrument_type]
    x = x+1

# Счет тинькофф
for i in tf.payload.positions:
    df.loc[x] = [i.figi, i.name, i.ticker, i.average_position_price.currency, i.balance, i.expected_yield.value, i.average_position_price.value, 'Tinkoff', i.instrument_type]
    x = x+1

# добавление рублевых активов портфеля
df.loc[x] = ['', 'Рубль', '', 'RUB', tf_rub.payload.currencies[1].balance, 0, 1, 'Tinkoff', 'Currency']
df.loc[x+1] = ['', 'Рубль', '', 'RUB', iis_rub.payload.currencies[1].balance, 0, 1, 'IIS', 'Currency']

# доб стоимость позиции с учетом курса валют на день выгрузки
df['position'] = df['balance'] * df['price'] + df['income']

# перевод валютных активов в рубли
df.loc[(df['currency'] == 'USD') & (df['ticker'] != 'USD000UTSTOM'), 'position'] *= usd
df.loc[(df['currency'] == 'EUR') & (df['ticker'] != 'EUR_RUB__TOM'), 'position'] *= eur

# перевод валюты в рубли
df.loc[df['ticker'] == 'USD000UTSTOM', 'position'] = (df['balance'] + df['income']) * usd
df.loc[df['ticker'] == 'EUR_RUB__TOM', 'position'] = (df['balance'] + df['income']) * eur

# делаем группировку по портфелю и типу актива, берем сумму позиций и сбрасываем индекс для плоского вида таблицы
dd = df.groupby(['portfolio', 'instrument_type']).sum().reset_index()
# добавляем текущую дату
dd['date'] = today.date()

# делаем выборку по нужным столбцам
dd = dd[['portfolio', 'instrument_type', 'position', 'date']]


# функция записи портфелей
def portfolio_write():
    pandas_gbq.to_gbq(df, table_name, project_id=project_id, if_exists='replace')


# функция записи стоимости портфелей на дату
def portfolio_value_write():
    pandas_gbq.to_gbq(dd, 'invest.portfolio_value', project_id=project_id, if_exists='append')

```

> В файле portfolio приведен код обращения к портфелям в Тинькоф инвестиции, преобразование их к табличному виду, обогащение данными и запись в таблицы `portfolio` и `portfolio_value`

---

### 6. создем python файл с именем deal и вставляем следующий код:  

```python
from datetime import datetime, timedelta
from pytz import timezone
from auth import client, broker_account_id_iis, broker_account_id_tf, project_id
from pycbrf.toolbox import ExchangeRates
import pandas as pd
import pandas_gbq

#  имя таблицы в формате 'имя схемы.имя таблицы'
table_name = 'invest.deal'
today = datetime.now(tz=timezone('Europe/Moscow'))
# получаем последний день, за которые были загрузки сделок
max_date_from_deal = pd.DataFrame(pandas_gbq.read_gbq(f"SELECT max(date) FROM {table_name}"))
d = str(max_date_from_deal['f0_'].iloc[0])
start_day = datetime.strptime(d, '%Y-%m-%d').replace(tzinfo=timezone('Europe/Moscow')) + timedelta(days=1)

# получаем сделки за период по портфелям
ops_iis = client.operations.operations_get(_from=start_day.isoformat(), to=today.isoformat(), broker_account_id=broker_account_id_iis)
ops_tf = client.operations.operations_get(_from=start_day.isoformat(), to=today.isoformat(), broker_account_id=broker_account_id_tf)
x = 0
df = pd.DataFrame(columns=['figi', 'date', 'instrument_type', 'currency', 'operation_type', 'payment', 'price', 'quantity', 'commission', 'portfolio'])


# выгрузка сделок для портфеля ИИС
for op in ops_iis.payload.operations:
    figi = op.figi
    date = op.date
    instrument_type = op.instrument_type
    currency = op.currency
    operation_type = op.operation_type
    curs = ExchangeRates(str(date.date()))
    # полученные и потраченные средства переводим в рубли по курсу на день сделки
    if currency == 'USD':
        payment = round(op.payment * float(curs['USD'].value), 2)
    elif currency == 'EUR':
        payment = round(op.payment * float(curs['EUR'].value), 2)
    else:
        payment = op.payment
    price = 0 if op.price is None else op.price
    quantity = 0 if op.quantity is None else op.quantity
    commission = 0 if op.commission is None else op.commission.value
    portfolio = 'IIS'
    df.loc[x] = [figi, date.date(), instrument_type, currency, operation_type, payment, price, quantity, commission, portfolio]
    x = x+1

# выгрузка сделок для портфеля Тинькоф
for op in ops_tf.payload.operations:
    figi = op.figi
    date = op.date
    instrument_type = op.instrument_type
    currency = op.currency
    operation_type = op.operation_type
    curs = ExchangeRates(str(date.date()))
    if currency == 'USD':
        payment = round(op.payment * float(curs['USD'].value), 2)
    elif currency == 'EUR':
        payment = round(op.payment * float(curs['EUR'].value), 2)
    else:
        payment = op.payment
    price = 0 if op.price is None else op.price
    quantity = 0 if op.quantity is None else op.quantity
    commission = 0 if op.commission is None else op.commission.value
    portfolio = 'Tinkoff'
    df.loc[x] = [figi, date.date(), instrument_type, currency, operation_type, payment, price, quantity, commission, portfolio]
    x = x+1


def deal_write():
    if df.empty:
        pass
    else:
        pandas_gbq.to_gbq(df, table_name, project_id=project_id, if_exists='append')

```

> В файле deal приведен код обращения к данным по сделкам в Тинькоф инвестициях по портфелям, в моём случае это основной портфель и ИИС

---

### 7. создем python файл с именем instruments и вставляем следующий код: 


```python
import pandas as pd
import pandas_gbq
from auth import client, project_id

x = 0
table_name = 'invest.instruments'
df = pd.DataFrame(columns=['currency', 'figi', 'isin', 'lot', 'min_price_increment', 'name', 'ticker', 'type'])

# Получение списка облигаций
bonds = client.market.market_bonds_get()
# Получение списка ETF
etfs = client.market.market_etfs_get()
# Получение списка акций
stocks = client.market.market_stocks_get()

# объединяем инструменты в один список
instr_list = bonds.payload.instruments + etfs.payload.instruments + stocks.payload.instruments

# формируем data frame
for i in instr_list:
    df.loc[x] = [i.currency, i.figi, i.isin, i.lot, i.min_price_increment, i.name, i.ticker, i.type]
    x = x+1


def instrument_write():
    pandas_gbq.to_gbq(df, table_name, project_id=project_id, if_exists='replace')

```

> В файле instruments приведен код получения всех инструментов торгуемых брокером Тинькоф

---

### 8. Запускаем программу

> Для запуска программы необходимо перейти в PyCharm перейти в файл main.py и нажать 
> зеленую стрелку слева сверху от окна редактора кода или вызвать контекстное меню и выбрать поле "Run main"  
> При успешном выполнении в консоли выйдет сообщение `Process finished with exit code 0`

# Аналитические отчеты

## Дашборд

> Аналитический отчет или дашборд будем создавать в бесплатном инструменте Google Data Studio.
Для доступа к нему нужен только аккаунт Google.  
Data Studio позволяет создавать сложные отчеты и имеет большой набор соединений к внешним источникам данных. 

### Начало работы с Google Data Studio

1. Переходим по ссылке [Google Data Studio](https://datastudio.google.com/)
2. Нажимаем "Создать" --> Источник данных --> Выбираем "BigQuery"
3. Выбираем созданный нами проект
4. Выбираем набор данных в котором создавали таблицы
5. Выбираем таблицу deal --> нажимаем "Связать" --> источник создан
6. Нажимаем значок "Студия данных"
7. Поочереди подключаем таблицы: portfolio и portfolio_value

Подробнее про подключение к BigQuery можно почитать здесь - [Connect to Google BigQuery](https://support.google.com/datastudio/answer/6370296#zippy=%2Cin-this-article)

---

### Создание и настройка дашборда

1. В главном меню студии данных нажимаем "Создать" --> "Отчет"
2. Даем отчету наименование
3. Нажимаем кнопку "Добавить данные"
4. Переходим во вкладку "Мои источники данных"
5. Выбираем поочереди источники, добавленные на предыдущем шаге 
6. удаляем автоматически добавленные диаграммы со страницы

Теперь есть все для наполнения дашборда.

### Создание диаграмм и фильтров отчета


## Мини-отчет 

> описание концепции

### Создание телеграм канала
- получение ид канала

### Создание телеграм бота

### Разворачивание бота в Google Cloud

### Настройка запуска бота по расписанию

# Релизы
[1]

# Ссылки

[1]: https://tinkoffcreditsystems.github.io/invest-openapi/
