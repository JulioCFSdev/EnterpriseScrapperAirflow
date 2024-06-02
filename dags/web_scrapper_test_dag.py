from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import json

def scrape_website():
    # URL do site de onde você quer extrair dados
    url = 'https://finance.yahoo.com/quote/MSFT'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Encontrar a informação desejada usando BeautifulSoup
    data = soup.find('h1', class_='svelte-3a2v0c').text.strip()
    print(data)
    
    # Retornar os dados encontrados
    return data

def save_to_json(ti):
    # Recuperar dados do retorno da função de scraping
    scraped_data = ti.xcom_pull(task_ids='scrape_website')
    
    # Estruturar os dados em formato JSON
    data_json = json.dumps({'informacao_important': scraped_data})
    
    # Salvar em um arquivo JSON
    with open('/opt/airflow/database/data.json', 'w') as f:
        f.write(data_json)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'web_scraping_to_json_dag',
    default_args=default_args,
    description='DAG para fazer web scraping e salvar em JSON',
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:
    
    scrape_website_task = PythonOperator(
        task_id='scrape_website',
        python_callable=scrape_website,
    )
    
    save_to_json_task = PythonOperator(
        task_id='save_to_json',
        python_callable=save_to_json,
    )

    scrape_website_task >> save_to_json_task
