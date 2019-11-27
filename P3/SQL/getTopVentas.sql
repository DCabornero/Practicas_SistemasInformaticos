CREATE OR REPLACE FUNCTION getTopVentas(anio INTEGER)
  RETURNS TABLE (
    agno INTEGER,
    pelicula VARCHAR,
    ventas INTEGER,
    prod_id INTEGER
  )
  AS $$
  BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (calc.agno) calc.agno, calc.pelicula, calc.ventas, calc.prod_id FROM(
      SELECT date_part('year', orders.orderdate)::INTEGER AS agno,
      imdb_movies.movietitle AS pelicula,
      SUM(orderdetail.quantity)::INTEGER AS ventas,
      products.prod_id AS prod_id
      FROM orders INNER JOIN orderdetail ON orderdetail.orderid = orders.orderid
      INNER JOIN products ON products.prod_id = orderdetail.prod_id
      INNER JOIN imdb_movies ON imdb_movies.movieid = products.movieid
      WHERE date_part('year', orders.orderdate) >= anio
      GROUP BY products.prod_id, agno, imdb_movies.movietitle
      ORDER BY agno, ventas DESC, pelicula
    ) AS calc;
  END; $$ LANGUAGE PLPGSQL;
