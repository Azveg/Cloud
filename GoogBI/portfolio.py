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

# запись стоимости портфеля на дату
# делаем группировку по портфелю и типу актива, берем сумму позиций и сбрасываем индекс для плоского вида таблицы
dd = df.groupby(['portfolio', 'instrument_type']).sum().reset_index()
# добавляем текущую дату
dd['date'] = today.date()

# делаем выборку по нужным столбцам
# print(dd[['portfolio', 'instrument_type', 'position', 'date']])
dd = dd[['portfolio', 'instrument_type', 'position', 'date']]


# функция записи портфелей
def portfolio_write():
    pandas_gbq.to_gbq(df, table_name, project_id=project_id, if_exists='replace')


# функция записи стоимости портфелей на дату
def portfolio_value_write():
    pandas_gbq.to_gbq(dd, 'invest.portfolio_value', project_id=project_id, if_exists='append')
