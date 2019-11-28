EXPLAIN
SELECT
  COUNT(DISTINCT customerid)
FROM
  orders
WHERE
  date_part('year', orderdate) = 2015 AND --Si se quiere cambiar el año, cambiar este número
  date_part('month', orderdate) = 04 AND  --Si se quiere cambiar el mes, ídem
  totalamount > 100; --Si se quiere cambiar el importe mínimo, ídem
