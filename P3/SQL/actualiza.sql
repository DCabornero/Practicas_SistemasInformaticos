ALTER TABLE customers ADD COLUMN saldo decimal DEFAULT 0 NOT NULL;
ALTER TABLE imdb_actormovies ADD PRIMARY KEY (actorid, movieid);
ALTER TABLE imdb_actormovies ADD CONSTRAINT imdb_actormovies_actorid_fkey FOREIGN KEY (actorid) REFERENCES imdb_actors (actorid);
ALTER TABLE imdb_actormovies ADD CONSTRAINT imdb_actormovies_movieid_fkey FOREIGN KEY (movieid) REFERENCES imdb_movies (movieid);

ALTER TABLE orders ALTER COLUMN netamount SET DEFAULT 0;
ALTER TABLE orders ALTER COLUMN totalamount SET DEFAULT 0;
ALTER TABLE orders ALTER COLUMN tax SET DEFAULT 15;
ALTER TABLE orders ALTER COLUMN orderdate SET DEFAULT CURRENT_DATE;

ALTER TABLE products ADD COLUMN stock NUMERIC DEFAULT 0;
ALTER TABLE products ADD COLUMN sales NUMERIC DEFAULT 0;
UPDATE products SET sales = inventory.sales, stock = inventory.stock FROM inventory WHERE products.prod_id = inventory.prod_id;

UPDATE products SET sales = calc.sales FROM (
  SELECT prod_id, sum(quantity) AS sales FROM orderdetail GROUP BY prod_id
) AS calc WHERE calc.prod_id = products.prod_id;

ALTER TABLE orderdetail ADD CONSTRAINT orderdetail_orderid_fkey FOREIGN KEY (orderid) REFERENCES orders (orderid);
ALTER TABLE orderdetail ADD CONSTRAINT orderdetail_prod_id_fkey FOREIGN KEY (prod_id) REFERENCES products (prod_id);

CREATE TABLE orderdetailaux AS SELECT orderid, prod_id, SUM(quantity) AS quantity FROM orderdetail GROUP BY orderid, prod_id HAVING COUNT(concat(prod_id,'-',orderid))>1;
DELETE FROM orderdetail WHERE EXISTS (SELECT * FROM orderdetailaux AS oda WHERE oda.orderid = orderdetail.orderid AND oda.prod_id = orderdetail.prod_id);
INSERT INTO orderdetail(orderid, prod_id, quantity) SELECT * FROM orderdetailaux;
DROP TABLE orderdetailaux;
ALTER TABLE orderdetail ADD PRIMARY KEY (orderid, prod_id);

UPDATE imdb_movies SET year = '1998' WHERE year = '1998-1999';

CREATE SEQUENCE languages_languageid_seq START 1;

CREATE TABLE languages(
  languageid int NOT NULL default nextval('languages_languageid_seq'::regclass) PRIMARY KEY,
  languagename varchar(30) NOT NULL);

INSERT INTO languages (languagename)
SELECT DISTINCT language FROM imdb_movielanguages;

ALTER TABLE imdb_movielanguages ADD COLUMN languageid integer;
ALTER TABLE imdb_movielanguages ADD CONSTRAINT imdb_movielanguages_languageid_fkey FOREIGN KEY (languageid) REFERENCES languages (languageid);
UPDATE imdb_movielanguages SET languageid = langtable.languageid FROM languages langtable WHERE language = langtable.languagename;
ALTER TABLE imdb_movielanguages DROP COLUMN language;
ALTER TABLE imdb_movielanguages ADD CONSTRAINT imdb_movielanguages_pkey PRIMARY KEY (movieid, languageid);

CREATE SEQUENCE countries_countryid_seq START 1;

CREATE TABLE countries(
  countryid int NOT NULL default nextval('countries_countryid_seq'::regclass) PRIMARY KEY,
  countryname varchar(50) NOT NULL);

INSERT INTO countries (countryname)
SELECT DISTINCT country FROM imdb_moviecountries;

ALTER TABLE imdb_moviecountries ADD COLUMN countryid integer;
ALTER TABLE imdb_moviecountries ADD CONSTRAINT imdb_moviecountries_countryid_fkey FOREIGN KEY (countryid) REFERENCES countries (countryid);
UPDATE imdb_moviecountries SET countryid = countrytable.countryid FROM countries countrytable WHERE country = countrytable.countryname;
ALTER TABLE imdb_moviecountries DROP COLUMN country;
ALTER TABLE imdb_moviecountries ADD CONSTRAINT imdb_moviecountries_pkey PRIMARY KEY (movieid, countryid);

CREATE SEQUENCE genres_genreid_seq START 1;

CREATE TABLE genres(
  genreid int NOT NULL default nextval('genres_genreid_seq'::regclass) PRIMARY KEY,
  genrename varchar(32) NOT NULL);

INSERT INTO genres (genrename)
SELECT DISTINCT genre FROM imdb_moviegenres;

ALTER TABLE imdb_moviegenres ADD COLUMN genreid integer;
ALTER TABLE imdb_moviegenres ADD CONSTRAINT imdb_moviegenres_genreid_fkey FOREIGN KEY (genreid) REFERENCES genres (genreid);
UPDATE imdb_moviegenres SET genreid = genretable.genreid FROM genres genretable WHERE genre = genretable.genrename;
ALTER TABLE imdb_moviegenres DROP COLUMN genre;
ALTER TABLE imdb_moviegenres ADD CONSTRAINT imdb_moviegenres_pkey PRIMARY KEY (movieid, genreid);

CREATE TABLE alerts(
  prod_id INT,
  PRIMARY KEY(prod_id),
  FOREIGN KEY (prod_id) REFERENCES products (prod_id)
);

DROP TABLE inventory;

ALTER TABLE customers ALTER COLUMN address1 DROP NOT NULL;
ALTER TABLE customers ALTER COLUMN city DROP NOT NULL;
ALTER TABLE customers ALTER COLUMN country DROP NOT NULL;
ALTER TABLE customers ALTER COLUMN region DROP NOT NULL;
ALTER TABLE customers ALTER COLUMN creditcardtype DROP NOT NULL;
ALTER TABLE customers ALTER COLUMN creditcardexpiration DROP NOT NULL;
ALTER TABLE customers ALTER COLUMN username DROP NOT NULL;
ALTER TABLE customers ALTER COLUMN gender SET NOT NULL;
ALTER TABLE customers ALTER COLUMN email SET NOT NULL;
ALTER TABLE customers ADD UNIQUE (email);

ALTER SEQUENCE customers_customerid_seq RESTART WITH 14094;
ALTER SEQUENCE orders_orderid_seq RESTART WITH 181791;
--Falta poner la foreign key de customers en orders
--Falta poner unique not null a los emails
