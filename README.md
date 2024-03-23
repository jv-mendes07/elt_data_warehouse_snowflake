# Projeto de Data Warehouse com Snowflake, DBT, Airflow, PostGreSQL & Looker Studio

Em tal projeto, modelo um **Data Warehouse** no **Snowflake** para às análises de negócio da concessionária fictícia **NovaDrive Motors**, uso o **Apache Airflow** para estruturar uma **DAG** em **Python** que extrai incrementalmente os dados brutos da concessionária do banco de dados transacional **PostGreSQL** e os carrega na camada intermediária (**Staging**) do **DWH**, com o **DBT**, transformo e trato tais dados brutos em análises que são disponibilizadas na camada analítica do **DWH** para compor o **dashboard** de **BI (Business Intelligence)** no **Looker Studio** para analisar às vendas de tal concessionária.

![](img/flux_of_project.png)

Basicamente, na primeira fase do projeto, tive que extrair os dados brutos do banco de dados transacional **PostGreSQL** de tais tabelas **vendas**, **vendedores**, **veiculos**, **estados**, **cidades**, **clientes** e **concessionarias**:

![](img/tables_in_postgresql.png)

Para realizar tal extração de dados brutos do banco de dados **PostGreSQL** do sistema transacional (**OLTP**) da concessionária, estruturei uma **DAG** no **Airflow** que extrai e ingere incrementalmente os dados brutos do **PostGreSQL** para a camada intermediária (**Staging**) do **Data Warehouse** no **Snowflake**:

![](img/dag_ingestion_post_gre_sql_to_snowflake.png)



