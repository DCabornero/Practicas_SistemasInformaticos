CREATE OR REPLACE FUNCTION getTopMonths(productos_min INTEGER, importe_min INTEGER)
  RETURNS TABLE (
    agno INTEGER,
    mes INTEGER,
    importe NUMERIC,
    productos INTEGER
  )
  AS $$
  BEGIN
    RETURN QUERY
    SELECT
      year,
      month,
      amount,
      prods
      FROM(
        SELECT
          date_part('year', orders.orderdate)::INTEGER AS year,
          date_part('month', orders.orderdate)::INTEGER AS month,
          SUM(orderdetail.quantity)::INTEGER AS prods
        FROM
          orders
            INNER JOIN
          orderdetail ON orderdetail.orderid = orders.orderid
        GROUP BY
          month,
          year
        ORDER BY
          year,
          month
    ) AS calc
      NATURAL JOIN (
      SELECT
        date_part('year', orders.orderdate)::INTEGER AS year,
        date_part('month', orders.orderdate)::INTEGER AS month,
        ROUND(SUM(orders.totalamount), 2) as amount
      FROM
        orders
      GROUP BY
        month,
        year
      ORDER BY
        year,
        month
    ) AS calc2
    WHERE
      calc2.amount > importe_min
        OR
      calc.prods > productos_min;
  END; $$ LANGUAGE PLPGSQL;
