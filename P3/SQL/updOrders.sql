CREATE OR REPLACE FUNCTION updOrds() RETURNS TRIGGER AS $$
  DECLARE
    more_prods INTEGER;
  BEGIN
    IF TG_OP = 'UPDATE' THEN
      UPDATE orders
      SET
        netamount = netamount + NEW.price * (NEW.quantity - OLD.quantity),
        orderdate = NOW()::date,
        totalamount = totalamount + ROUND((NEW.price * (NEW.quantity - OLD.quantity))*(1 + tax/100), 2)
      WHERE
        orderid = NEW.orderid;
    ELSIF TG_OP = 'INSERT' THEN
      UPDATE orders
      SET
        netamount = netamount + NEW.price * NEW.quantity,
        orderdate = NOW()::date,
        totalamount = totalamount + ROUND((NEW.price * NEW.quantity)*(1 + tax/100), 2)
      WHERE
        orderid = NEW.orderid;
    ELSE
      UPDATE orders
      SET
        netamount = netamount - OLD.price * OLD.quantity,
        orderdate = NOW()::date,
        totalamount = totalamount - ROUND((OLD.price * OLD.quantity)*(1 + tax/100), 2)
      WHERE
       orderid = OLD.orderid;
    END IF;
  RETURN NEW;
  END;
$$ LANGUAGE PLPGSQL;

CREATE TRIGGER updOrders AFTER INSERT OR UPDATE OR DELETE ON orderdetail
FOR EACH ROW EXECUTE PROCEDURE updOrds();
