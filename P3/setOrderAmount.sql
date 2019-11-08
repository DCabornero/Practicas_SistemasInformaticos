CREATE OR REPLACE FUNCTION setOrderAmount() RETURNS VOID AS $$
  BEGIN
    UPDATE orders SET netamount = calc.total, totalamount = ROUND((calc.total*(tax+100)/100), 2) FROM
      (SELECT orderid, SUM(price) AS total FROM orderdetail GROUP BY orderid) AS calc
        WHERE orders.orderid = calc.orderid;
  END; $$ LANGUAGE PLPGSQL;
