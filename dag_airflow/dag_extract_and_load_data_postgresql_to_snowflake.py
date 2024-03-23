# Importação das bibliotecas que serão usadas para extrair os dados de cada tabela no PostGreSQL
# e carrega-los para às tabelas de destino na área de Stage no Data Warehouse:

from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
import pandas as pd
import psycopg2


# Definição de configurações da DAG:

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes = 5)
}

# Instanciação da DAG de extração e carregamento incremental de dados do banco de dados PostGreSQL para
# a tabela de destino no Data Warehouse no Snowflake:

@dag(
    dag_id = 'extract_and_load_data_postgresql_to_snowflake',
    default_args = default_args,
    description = 'Load data incrementally from PostGreSQL to Snowflake',
    schedule_interval = timedelta(days = 1),
    catchup = False
)

# Função Python que itera sobre cada tabela no banco de dados transacional do PostGreSQL, extrai os dados 
# e os carrega em lote com o uso da biblioteca Pandas para às tabelas de destino no Data Warehouse na área de Stage
# no Snowflake:

def postgres_to_snowflake_etl():
    table_names = ['veiculos', 'estados', 'concessionarias', 'vendedores', 'clientes', 'vendas', 'cidades']
    
    # Conexão com o banco de dados PostGreSQL da NovaDrive Motors:

    postgre_conn = psycopg2.connect(
    host="159.223.187.110",
    database="novadrive",
    user="etlreadonly",
    password="novadrive376A@"
    )

    # Tarefa de iteração sobre cada tabela do banco de dados transacional PostGreSQL, 
    # para extrair o ID máximo de cada tabela no DWH do Snowflake,
    # para extrair e carregar somente dados novos da fonte com um ID maior do que o ID máximo registrado na tabela de destino:

    for table_name in table_names:
        @task(task_id = f'get_max_id_{table_name}')
        def get_max_primary_key(table_name: str):
            with SnowflakeHook(snowflake_conn_id='snowflake').get_conn() as snowflake_conn:
                with snowflake_conn.cursor() as cursor: 
                    cursor.execute(f'SELECT MAX(ID_{table_name}) FROM {table_name}')
                    max_id = cursor.fetchone()[0]
                    return max_id if max_id is not None else 0

        # Tarefa de extração de dados novos da fonte do PostGreSQL com um ID maior do que o ID máximo extraído da tabela de destino no Snowflake,
        # construção da query em SQL com o uso da biblioteca Pandas para realizar o carregamento em lote de uma vez para a área de Stage
        # no Data Warehouse: 

        @task(task_id = f'load_data_{table_name}')
        def load_incremental_data(table_name: str, max_id: int):
            with postgre_conn.cursor() as pg_cursor:
                primary_key = f'ID_{table_name}'

                pg_cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
                columns = [row[0] for row in pg_cursor.fetchall()]
                columns_list_str = ', '.join(columns)
                placeholders = ', '.join(['%s'] * len(columns))

                query_postgre_sql = f'SELECT {columns_list_str} FROM {table_name} WHERE {primary_key} > {max_id}'
                pg_cursor.execute(query_postgre_sql)
                rows = pg_cursor.fetchall()
                df_source = pd.DataFrame(rows, columns=columns)

                # Se não haver dados novos, a DAG será finalizada, caso contrário o carregamento será feito para a tabela de destino 
                # na área de Stage no DWH do Snowflake:

                if df_source.shape[0] == 0:
                    pass
                else:
                    with SnowflakeHook(snowflake_conn_id='snowflake').get_conn() as snowflake_conn:

                        for col in df_source.select_dtypes(include=['object', 'datetime64[ns, UTC]']).columns:
                            df_source[col] = df_source[col].apply(lambda x: f"'{x}'")
                        
                        values_list = df_source.values.tolist()
                        values_str = ', '.join([f"({', '.join(map(str, row))})" for row in values_list])

                        with snowflake_conn.cursor() as sf_cursor:

                            insert_query = f"INSERT INTO {table_name} ({columns_list_str}) VALUES {values_str}"

                            sf_cursor.execute(insert_query)

        # Chamada da funções Python que extrai o ID máximo da tabela de destino, e ingere somente dados novos da fonte com um ID maior do 
        # que o que foi registrado na tabela de destino no Snowflake:

        max_id = get_max_primary_key(table_name)
        load_incremental_data(table_name, max_id)

# Chamada da função que irá executar toda a extração e carga de dados novos do PostGreSQL para a área de Stage no DWH do Snowflake:

postgres_to_snowflake_etl_dag = postgres_to_snowflake_etl()