{{ config(materialized = 'table')}}
SELECT  
    DATE_TRUNC('month', v.data_venda) AS mes_venda,
    COUNT(v.venda_id) AS quantidade_vendas,
    SUM(v.valor_venda) AS faturamento,
    AVG(v.valor_venda) AS faturamento_medio
FROM
    {{ ref('fct_vendas') }} v
GROUP BY
    DATE_TRUNC('month', v.data_venda)
ORDER BY 
    mes_venda ASC
