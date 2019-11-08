UPDATE orderdetail SET price = calc.price FROM
  (select products.prod_id AS prod_id, orders.orderid AS orderid,
    ROUND((products.price/(POWER(1.02, date_part('year', now()::date) - date_part('year', orderdate))))::NUMERIC, 2) as price from
    orderdetail inner join products on orderdetail.prod_id = products.prod_id
      inner join orders on orderdetail.orderid = orders.orderid) AS calc
        WHERE orderdetail.prod_id = calc.prod_id and orderdetail.orderid = calc.orderid;