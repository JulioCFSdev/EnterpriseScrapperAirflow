from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

# Função que será executada pela tarefa
def print_hello():
    print("Olá, Airflow está funcionando!")

# Definição padrão de argumentos que serão aplicados a todas as tarefas na DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Criação da DAG, que define como as tarefas são organizadas e gerenciadas
with DAG(
    'hello_world_dag',        # Nome da DAG
    default_args=default_args,
    description='Uma DAG simples para testar o ambiente Airflow',
    schedule_interval=timedelta(days=1),  # Intervalo de agendamento, aqui definido para executar uma vez por dia
    catchup=False             # Se deve ou não "pegar" as instâncias não executadas se o start_date for no passado
) as dag:

    # Definição da tarefa que executa a função print_hello
    hello_task = PythonOperator(
        task_id='print_hello',
        python_callable=print_hello,
    )

# hello_task é a única tarefa e, portanto, não tem tarefas anteriores ou subsequentes

