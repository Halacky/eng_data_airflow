from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import os
from transform_script import transform

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')
PROFIT_TABLE_PATH = os.path.join(DATA_DIR, 'profit_table.csv')
FLAGS_OUTPUT_PATH = os.path.join(DATA_DIR, 'flags_activity.csv')

PRODUCTS = list("abcdefghij")
CALC_DATE = "2024-03-01" 

def extract():
    df = pd.read_csv(PROFIT_TABLE_PATH)
    temp_path = os.path.join(DATA_DIR, 'temp_extracted.csv')
    df.to_csv(temp_path, index=False)
    return temp_path

def transform_product(product, **context):
    temp_path = context['ti'].xcom_pull(task_ids='extract_data')
    df = pd.read_csv(temp_path)
    
    flags_df = transform(df, CALC_DATE, product)

    flags_df['calc_date'] = CALC_DATE

    product_path = os.path.join(DATA_DIR, f'flags_{product}.csv')
    flags_df.to_csv(product_path, index=False)
    return product_path

def load_combined(**context):
    dfs = []
    for product in PRODUCTS:
        product_path = context['ti'].xcom_pull(task_ids=f'transform_{product}')
        df = pd.read_csv(product_path)
        dfs.append(df)

    result_df = pd.concat(dfs)

    if os.path.exists(FLAGS_OUTPUT_PATH):
        old_df = pd.read_csv(FLAGS_OUTPUT_PATH)
        old_df = old_df[old_df['calc_date'] != CALC_DATE]
        
        result_df = pd.concat([old_df, result_df], ignore_index=True)

    result_df.to_csv(FLAGS_OUTPUT_PATH, index=False)

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='etl_flags_parallel_Kirill_Golovan',
    start_date=datetime(2024, 4, 5),
    schedule_interval='0 0 5 * *',
    catchup=False,
    default_args=default_args,
    description='ETL по флагам активности с параллельной трансформацией по продуктам',
) as dag:

    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract,
    )

    transform_tasks = []
    for product in PRODUCTS:
        t = PythonOperator(
            task_id=f'transform_{product}',
            python_callable=transform_product,
            provide_context=True,
            op_kwargs={'product': product},
        )
        transform_tasks.append(t)

    load_task = PythonOperator(
        task_id='load_flags',
        python_callable=load_combined,
        provide_context=True,
    )

    extract_task >> transform_tasks >> load_task