CREATE OR REPLACE FUNCTION updOrds() RETURNS TRIGGER AS $$
  DECLARE
    more_prods INTEGER;
  BEGIN
    IF TG_OP = 'INSERT' or TG_OP = 'UPDATE' THEN
      UPDATE orders
      SET netamount = netamount + NEW.price * NEW.quantity,
      orderdate = NOW()::date
      WHERE orderid = NEW.orderid;
    ELSE
      SELECT COUNT(*) INTO more_prods FROM orderdetail WHERE orderdetail.orderid = OLD.orderid;
      IF more_prods > 0 THEN
        UPDATE orders
        SET netamount = netamount - OLD.price * OLD.quantity,
        orderdate = NOW()::date
        WHERE orderid = OLD.orderid;
      --ELSE
        --DELETE FROM orders
        --WHERE orderid = OLD.orderid;
      END IF;
    END IF;
  RETURN NEW;
  END;
$$ LANGUAGE PLPGSQL;

CREATE TRIGGER updOrders AFTER INSERT OR UPDATE OR DELETE ON orderdetail
FOR EACH ROW EXECUTE PROCEDURE updOrds();
