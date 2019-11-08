CREATE OR REPLACE FUNCTION getTopVentas(anio INTEGER)
  RETURNS TABLE (
    agno INTEGER,
    pelicula VARCHAR,
    ventas INTEGER
  )
  AS $$
  BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (calc.agno) calc.agno, calc.pelicula, calc.ventas FROM(
      SELECT date_part('year', orders.orderdate)::INTEGER AS agno,
      imdb_movies.movietitle AS pelicula,
      SUM(orderdetail.quantity)::INTEGER AS ventas
      FROM orders INNER JOIN orderdetail ON orderdetail.orderid = orders.orderid
      INNER JOIN products ON products.prod_id = orderdetail.prod_id
      INNER JOIN imdb_movies ON imdb_movies.movieid = products.movieid
      WHERE date_part('year', orders.orderdate) >= anio
      GROUP BY imdb_movies.movieid, agno
      ORDER BY agno, ventas DESC, pelicula
    ) AS calc;
  END; $$ LANGUAGE PLPGSQL;
