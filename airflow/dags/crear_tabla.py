from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.providers.postgres.hooks.postgres import PostgresHook
import requests
import json
import pandas as pd
import numpy as np

default_args = {
    'owner': 'user',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 28),
    'email': ['user@mail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('Crear_tabla', schedule_interval="@once", default_args=default_args)

def get_data(**kwargs):
    url = "http://10.43.101.149/data?group_number=8"
    resp = requests.get(url)
    if resp.status_code == 200:
        res = resp.json()
        return res
    return -1

def save_db(**kwargs):
    query = 'SELECT * FROM test_table'
    postgres_hook = PostgresHook(postgres_conn_id='postgres_test_conn', schema='airflow')
    connection = postgres_hook.get_conn()
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    for result in results:
        print("*********", result)

def check_table_exists(**kwargs):
    query = 'SELECT COUNT(*) FROM information_schema.tables WHERE table_name=\'test_table\''
    postgres_hook = PostgresHook(postgres_conn_id='postgres_test_conn', schema='airflow')
    connection = postgres_hook.get_conn()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0] ; # Devuelve directamente el entero


def store_data(**kwargs):
    res = get_data()
    table_status = check_table_exists()
    postgres_hook = PostgresHook(postgres_conn_id='postgres_test_conn', schema='airflow')

    if table_status == 0:
        print("----- table does not exist, creating it")
        create_sql = """
        CREATE TABLE test_table (
            Elevation VARCHAR(255),
            Aspect VARCHAR(255),
            Slope VARCHAR(255),
            Horizontal_Distance_To_Hydrology VARCHAR(255),
            Vertical_Distance_To_Hydrology VARCHAR(255),
            Horizontal_Distance_To_Roadways VARCHAR(255),
            Hillshade_9am VARCHAR(255),
            Hillshade_Noon VARCHAR(255),
            Hillshade_3pm VARCHAR(255),
            Horizontal_Distance_To_Fire_Points VARCHAR(255),
            Wilderness_Area VARCHAR(255),
            Soil_Type VARCHAR(255),
            Cover_Type VARCHAR(255)
        );
        """
        postgres_hook.run(create_sql)
    else:
        print("---- table already exists")

    if res != -1:
        for data in res["data"]:
            sql = 'INSERT INTO test_table VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            postgres_hook.run(sql, parameters=tuple(data))

    df = postgres_hook.get_pandas_df(sql="SELECT * FROM test_table;")
    df.to_csv('/opt/airflow/data/cross_table.csv', index=False)


py = PythonOperator(
    task_id='py_opt',
    python_callable=save_db,
    dag=dag,
)

py1 = PythonOperator(
    task_id='store_opt',
    python_callable=store_data,
    dag=dag,
)

t1 = BashOperator(
    task_id='task_1',
    bash_command='echo "Hello World from Task 1"',
    dag=dag
)

t1 >> py1  # Primero t1, luego py1
py1 >> py  # Asegurarse que py1 se complete antes de ejecutar py
