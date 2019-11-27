--Añadimos la columna del saldo
ALTER TABLE customers
  ADD COLUMN saldo decimal DEFAULT 50 NOT NULL;

--Actualizamos las keys en actormovies
ALTER TABLE imdb_actormovies
  ADD PRIMARY KEY (actorid, movieid);
ALTER TABLE imdb_actormovies
  ADD CONSTRAINT imdb_actormovies_actorid_fkey
    FOREIGN KEY (actorid)
      REFERENCES imdb_actors (actorid);
ALTER TABLE imdb_actormovies
  ADD CONSTRAINT imdb_actormovies_movieid_fkey
    FOREIGN KEY (movieid)
      REFERENCES imdb_movies (movieid);

--Añadimos defaults a columnas necesarias
ALTER TABLE orders
  ALTER COLUMN netamount
    SET DEFAULT 0;
ALTER TABLE orders
  ALTER COLUMN totalamount
    SET DEFAULT 0;
ALTER TABLE orders
  ALTER COLUMN tax
    SET DEFAULT 15;
ALTER TABLE orders
  ALTER COLUMN orderdate
    SET DEFAULT CURRENT_DATE;

--Añadimos las columnas necesarias en products para mergear inventory en products
ALTER TABLE products
  ADD COLUMN stock NUMERIC
    DEFAULT 20;
ALTER TABLE products
  ADD COLUMN sales NUMERIC
    DEFAULT 0;

--Se actualizan las ventas de los productos con las indicadas en el inventario
UPDATE products
  SET
    sales = inventory.sales,
    stock = inventory.stock
  FROM
    inventory
  WHERE
    products.prod_id = inventory.prod_id;

--Cálculo de ventas de los productos según orderdetail
UPDATE products
  SET
    sales = calc.sales
  FROM (
    SELECT
      prod_id,
      sum(quantity)
    AS
      sales
    FROM
      orderdetail
    GROUP BY
      prod_id
    ) AS calc
  WHERE
    calc.prod_id = products.prod_id;


--Añadimos las keys necesarias a orderdetail
ALTER TABLE orderdetail
  ADD CONSTRAINT orderdetail_orderid_fkey
    FOREIGN KEY (orderid)
      REFERENCES orders (orderid);
ALTER TABLE orderdetail
  ADD CONSTRAINT orderdetail_prod_id_fkey
    FOREIGN KEY (prod_id)
      REFERENCES products (prod_id);

--Añadimos la foreign key de customerid en orders
ALTER TABLE orders
  ADD CONSTRAINT orders_customerid_fkey
    FOREIGN KEY (customerid)
      REFERENCES customers (customerid);

--Creamos una tabla auxiliar donde guardamos todos los orderid y prod_id.
--En caso de que haya dos elementos con el mismo orderid y prod_id, sumamos su
--precio en orderdetailaux, dropeamos ese dato de orderdetail y posteriormente
--mergeamos ambas tablas
CREATE TABLE
  orderdetailaux
    AS
      SELECT
        orderid,
        prod_id,
        SUM(quantity) AS quantity
      FROM
        orderdetail
      GROUP BY
        orderid,
        prod_id
      HAVING
        COUNT(concat(prod_id,'-',orderid))>1;

DELETE
  FROM
    orderdetail
  WHERE
    EXISTS (
        SELECT *
        FROM
          orderdetailaux AS oda
        WHERE
          oda.orderid = orderdetail.orderid AND
          oda.prod_id = orderdetail.prod_id
    );

INSERT INTO
  orderdetail(orderid, prod_id, quantity)
    SELECT *
    FROM
      orderdetailaux;

DROP TABLE orderdetailaux;

ALTER TABLE
  orderdetail
    ADD PRIMARY KEY (orderid, prod_id);

--Quitamos el único caso en el que el año es un intervalo
UPDATE imdb_movies
  SET
    year = '1998'
  WHERE
    year = '1998-1999';

--Creamos una secuencia para los ids de la tabla de languages
CREATE SEQUENCE languages_languageid_seq START 1;

--Creamos la tabla de languages
CREATE TABLE
  languages(
    languageid int NOT NULL
      default nextval('languages_languageid_seq'::regclass) PRIMARY KEY,
    languagename varchar(30) NOT NULL
  );

--Insertamos los valores de lenguaje
INSERT INTO languages (languagename)
SELECT DISTINCT language FROM imdb_movielanguages;

--Hacemos las sustituciones en las relaciones y añadimos las correspondientes
--keys en imdb_movielanguages
ALTER TABLE imdb_movielanguages
    ADD COLUMN languageid integer;

ALTER TABLE imdb_movielanguages
  ADD CONSTRAINT imdb_movielanguages_languageid_fkey
    FOREIGN KEY (languageid)
      REFERENCES languages (languageid);

UPDATE imdb_movielanguages
  SET
    languageid = langtable.languageid
  FROM
    languages
    langtable
  WHERE
    language = langtable.languagename;

ALTER TABLE imdb_movielanguages
  DROP COLUMN language;

ALTER TABLE imdb_movielanguages
  ADD CONSTRAINT imdb_movielanguages_pkey
    PRIMARY KEY (movieid, languageid);

--Creamos una secuencia para los ids de la tabla de countries
CREATE SEQUENCE countries_countryid_seq START 1;

--Creamos la tabla de countries
CREATE TABLE countries(
  countryid int NOT NULL
    default nextval('countries_countryid_seq'::regclass) PRIMARY KEY,
  countryname varchar(50) NOT NULL
  );

--Insertamos los valores de countries
INSERT INTO countries (countryname);
SELECT DISTINCT country FROM imdb_moviecountries;

--Actualizamos las keys de imdb_moviecountries
ALTER TABLE imdb_moviecountries
  ADD COLUMN countryid integer;

ALTER TABLE imdb_moviecountries
  ADD CONSTRAINT imdb_moviecountries_countryid_fkey
    FOREIGN KEY (countryid)
      REFERENCES countries (countryid);

UPDATE imdb_moviecountries
  SET
    countryid = countrytable.countryid
  FROM
    countries countrytable
  WHERE
    country = countrytable.countryname;

ALTER TABLE imdb_moviecountries
  DROP COLUMN country;

ALTER TABLE imdb_moviecountries
  ADD CONSTRAINT imdb_moviecountries_pkey
    PRIMARY KEY (movieid, countryid);

--Creamos una secuencia para la tabla de genres
CREATE SEQUENCE genres_genreid_seq START 1;

--Creamos la tabla de genres
CREATE TABLE genres(
  genreid int NOT NULL default nextval('genres_genreid_seq'::regclass) PRIMARY KEY,
  genrename varchar(32) NOT NULL);

--Insertamos los valores
INSERT INTO genres (genrename)
SELECT
  DISTINCT
    genre
  FROM
    imdb_moviegenres;

--Hacemos las sustituciones en las relaciones y añadimos las keys a moviegenres
ALTER TABLE imdb_moviegenres
  ADD COLUMN
    genreid integer;

ALTER TABLE imdb_moviegenres
  ADD CONSTRAINT imdb_moviegenres_genreid_fkey
    FOREIGN KEY (genreid)
      REFERENCES genres (genreid);

UPDATE imdb_moviegenres
  SET
    genreid = genretable.genreid
  FROM
    genres
    genretable
  WHERE
    genre = genretable.genrename;

ALTER TABLE imdb_moviegenres DROP COLUMN genre;
ALTER TABLE imdb_moviegenres
  ADD CONSTRAINT imdb_moviegenres_pkey
    PRIMARY KEY (movieid, genreid);

--Creamos la tabla de alerts
CREATE TABLE alerts(
  prod_id INT,
  PRIMARY KEY(prod_id),
  FOREIGN KEY (prod_id)
      REFERENCES products (prod_id)
);

--Borramos el inventario ya que está mergeado en products
DROP TABLE inventory;

--Quitamos constraints not null en datos que no usamos
ALTER TABLE customers
  ALTER COLUMN address1 DROP NOT NULL;
ALTER TABLE customers
  ALTER COLUMN city DROP NOT NULL;
ALTER TABLE customers
  ALTER COLUMN country DROP NOT NULL;
ALTER TABLE customers
  ALTER COLUMN region DROP NOT NULL;
ALTER TABLE customers
  ALTER COLUMN creditcardtype DROP NOT NULL;
ALTER TABLE customers
  ALTER COLUMN creditcardexpiration DROP NOT NULL;
ALTER TABLE customers
  ALTER COLUMN username DROP NOT NULL;
ALTER TABLE customers
  ALTER COLUMN gender SET NOT NULL;
ALTER TABLE customers
  ALTER COLUMN email SET NOT NULL;

--Añadimos la constraint unique en email ya que lo usamos de identificador y
--no hay ningún email repetido
ALTER TABLE customers
  ADD UNIQUE (email);

--Reiniciamos las secuencias en el valor más alto existente para poder utilizarlas
--para insertar nuevos datos
ALTER SEQUENCE customers_customerid_seq
  RESTART WITH 14094;
ALTER SEQUENCE orders_orderid_seq
  RESTART WITH 181791;
