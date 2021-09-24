from openapi_client import openapi
from google.oauth2 import service_account
import pandas_gbq

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
