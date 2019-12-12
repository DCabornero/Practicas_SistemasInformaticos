ALTER TABLE customers ADD COLUMN promo SMALLINT CONSTRAINT valid_perc CHECK(promo >= 0 AND promo <= 100);

CREATE OR REPLACE FUNCTION updProm() RETURNS TRIGGER AS $$
  BEGIN
    UPDATE orderdetail
    SET
      price = products.price - (products.price*(NEW.promo/100))
    FROM
      customers NATURAL JOIN orders NATURAL JOIN orderdetail NATURAL JOIN products
    WHERE
      orders.customerid = NEW.customerid
    AND
      orders.status IS NULL;
    UPDATE orders
    SET
      netamount = calc.total,
      totalamount = ROUND((calc.total*(tax+100)/100), 2)
    FROM
      (SELECT
        orderid,
        SUM(price) AS total
      FROM
        orderdetail
      GROUP BY
        orderid) AS calc
    WHERE orders.orderid = calc.orderid;
    -- Para el deadlock
    PERFORM pg_sleep(60);
    UPDATE orderdetail
    SET
      price = price;
  RETURN NEW;
  END;
$$ LANGUAGE PLPGSQL;

CREATE TRIGGER updPromo AFTER UPDATE ON customers
FOR EACH ROW EXECUTE PROCEDURE updProm();
