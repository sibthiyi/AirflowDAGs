from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import requests
import psycopg2

default_args = {
  'owner': 'airflow',
  'start_date': datetime(2023, 10, 26),
  'retries': 1,
}

dag = DAG(
  'openaq_data_pipeline',
  default_args=default_args,
  description='Retrieve, transform, and store OpenAQ data',
  schedule_interval='0 4 * * *',
  catchup=False,
  tags=['openaq'],
)

def fetch_transform_store_openaq_data():
  url = "https://api.openaq.org/v2/locations?page=1&offset=0&sort=desc&radius=1000&country=ID&location=Jakarta%20Central&order_by=lastUpdated&dump_raw=false"
  headers = {"accept": "application/json"}

  response = requests.get(url, headers=headers)
  data = response.json()

  host = 'postgres'
  port = 5432
  database = 'airflow'
  username = 'airflow'
  password = 'airflow'

  conn = psycopg2.connect(host=host, port=port, database=database, user=username, password=password)
  cur = conn.cursor()

  for result in data['results']:
    cur.execute(
      "INSERT INTO airquality (city, name, country) VALUES (%s, %s, %s)",
      (result.get('city'), result.get('name'), result.get('country'))
    )

  conn.commit()
  cur.close()
  conn.close()

fetch_transform_store_task = PythonOperator(
  task_id='fetch_transform_store_openaq',
  python_callable=fetch_transform_store_openaq_data,
  dag=dag,
)

fetch_transform_store_task