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
