from google.oauth2 import service_account
import pandas_gbq

project_id = 'my_project_id'
credentials = service_account.Credentials.from_service_account_file('credentials.json')
table_from = 'my_project_id.my_data_set.my_table'

pandas_gbq.context.credentials = credentials
pandas_gbq.context.project = project_id


def select_big_query():
    return pandas_gbq.read_gbq(f"SELECT context_0, reply FROM `{table_from}`")
