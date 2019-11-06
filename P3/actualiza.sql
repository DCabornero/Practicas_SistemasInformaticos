ALTER TABLE customers ADD COLUMN saldo decimal DEFAULT 0;
ALTER TABLE imdb_actormovies ADD PRIMARY KEY (actorid, movieid);
ALTER TABLE imdb_actormovies ADD CONSTRAINT imdb_actormovies_actorid_fkey FOREIGN KEY (actorid) REFERENCES imdb_actors (actorid);
ALTER TABLE imdb_actormovies ADD CONSTRAINT imdb_actormovies_movieid_fkey FOREIGN KEY (movieid) REFERENCES imdb_movies (movieid);

ALTER TABLE orderdetail ADD CONSTRAINT orderdetail_orderid_fkey FOREIGN KEY (orderid) REFERENCES orders (orderid);
ALTER TABLE orderdetail ADD CONSTRAINT orderdetail_prod_id_fkey FOREIGN KEY (prod_id) REFERENCES products (prod_id);
--SELECT orderid, prod_id, price, SUM(quantity) AS quantity FROM orderdetail GROUP BY orderid, prod_id, price; Falta sustituirlo
--ALTER TABLE orderdetail ADD PRIMARY KEY (orderid, prod_id);

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
