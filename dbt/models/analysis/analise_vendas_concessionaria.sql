{{ config(materialized = 'table')}}
SELECT  
    con.concessionaria_id AS id,
    con.concessionaria,
    cid.nome_cidade AS cidade,
    est.nome_estado AS estado,
    COUNT(v.venda_id) AS quantidade_vendas,
    SUM(v.valor_venda) AS faturamento,
    AVG(v.valor_venda) AS faturamento_medio
FROM
    {{ ref('fct_vendas') }} v
JOIN
    {{ ref('dim_concessionarias')}} con
ON
    v.concessionaria_id = con.concessionaria_id
JOIN
    {{ ref('dim_cidades')}} cid 
ON
    cid.cidade_id = con.cidade_id
JOIN
    {{ ref('dim_estados')}} est
ON 
    est.estado_id = cid.estado_id
GROUP BY
    con.concessionaria_id,
    con.concessionaria,
    cid.nome_cidade,
    est.nome_estado
ORDER BY 
    faturamento DESC
