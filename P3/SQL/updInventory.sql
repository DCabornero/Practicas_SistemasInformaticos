CREATE OR REPLACE FUNCTION updInv() RETURNS TRIGGER AS $$
  DECLARE
    auxrec RECORD;
    final INTEGER;
  BEGIN
    FOR auxrec IN
      SELECT
        prod_id,
        quantity
      FROM
        orderdetail
      WHERE
        orderid = OLD.orderid
    LOOP
      UPDATE products
        SET
          stock = stock - auxrec.quantity,
          sales = sales + auxrec.quantity
        WHERE
          products.prod_id = auxrec.prod_id;
      final := (SELECT stock FROM products WHERE products.prod_id = auxrec.prod_id);
      IF final = 0 THEN
        INSERT INTO alerts(prod_id)
          VALUES (auxrec.prod_id);
      END IF;
    END LOOP;
    UPDATE orders
      SET
        orderdate = NOW()::date
      WHERE
        OLD.orderid = orders.orderid;
    RETURN NEW;
  END;
$$ LANGUAGE PLPGSQL;

CREATE TRIGGER updInventory AFTER UPDATE OF status ON orders
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE PROCEDURE updInv();
