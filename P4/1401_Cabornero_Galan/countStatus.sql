EXPLAIN select count(*) from orders where status is null;

EXPLAIN select count(*) from orders where status ='Shipped';

CREATE INDEX ord ON orders(status);

EXPLAIN select count(*) from orders where status is null;

EXPLAIN select count(*) from orders where status ='Shipped';

ANALYZE orders;

EXPLAIN select count(*) from orders where status is null;

EXPLAIN select count(*) from orders where status ='Shipped';
