UPDATE 
  orderdetail
SET
  price = calc.price
FROM
  (SELECT
    products.prod_id AS prod_id,
    orders.orderid AS orderid,
    ROUND((products.price/(POWER(1.02, date_part('year', now()::date) - date_part('year', orderdate))))::NUMERIC, 2) AS price
  FROM
    orderdetail
      INNER JOIN
    products ON orderdetail.prod_id = products.prod_id
      INNER JOIN
    orders ON orderdetail.orderid = orders.orderid) AS calc
  WHERE orderdetail.prod_id = calc.prod_id and orderdetail.orderid = calc.orderid;
