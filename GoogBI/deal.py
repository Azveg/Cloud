from datetime import datetime, timedelta
from pytz import timezone
from auth import client, broker_account_id_iis, broker_account_id_tf, project_id
from pycbrf.toolbox import ExchangeRates
import pandas as pd
import pandas_gbq


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
