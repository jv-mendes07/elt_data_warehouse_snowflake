{{ config(materialized = 'table')}}
SELECT  
    ven.vendedor_id AS id,
    ven.nome_vendedor AS vendedor,
    c.concessionaria AS concessionaria,
    COUNT(v.venda_id) AS quantidade_vendas,
    SUM(v.valor_venda) AS faturamento,
    AVG(v.valor_venda) AS faturamento_medio
FROM
    {{ ref('fct_vendas') }} v
JOIN
    {{ ref('dim_vendedores')}} ven
ON
    v.vendedor_id = ven.vendedor_id
JOIN
    {{ ref('dim_concessionarias')}} c
ON
    c.concessionaria_id = ven.concessionaria_id
GROUP BY
    ven.vendedor_id,
    ven.nome_vendedor,
    c.concessionaria
ORDER BY 
    faturamento DESC
