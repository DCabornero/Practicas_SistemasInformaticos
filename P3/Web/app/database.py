import os
import sys, traceback
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.sql import select, insert, join
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1?client_encoding=utf8", echo=False)
db_meta = MetaData(bind=db_engine)
# cargar una tabla
db_cust = Table('customers', db_meta, autoload=True, autoload_with=db_engine)
db_films = Table('imdb_movies', db_meta, autoload=True, autoload_with=db_engine)
db_dirfilm = Table('imdb_directormovies', db_meta, autoload=True, autoload_with=db_engine)
db_actfilm = Table('imdb_actormovies', db_meta, autoload=True, autoload_with=db_engine)
db_dirs = Table('imdb_directors', db_meta, autoload=True, autoload_with=db_engine)
db_acts = Table('imdb_actors', db_meta, autoload=True, autoload_with=db_engine)
db_genres = Table('genres', db_meta, autoload=True, autoload_with=db_engine)
db_genfilm = Table('imdb_moviegenres', db_meta, autoload=True, autoload_with=db_engine)

def db_login(email, password):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_login = select([db_cust]).where(text("email = '{0}' and password = '{1}'".format(email, password)))
        db_result = db_conn.execute(db_login)

        db_conn.close()

        return list(db_result)
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def db_registro(email, password, gender, name, creditcard, surname):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_registro = db_cust.insert().values(email=email, password=password,
                            gender=gender, firstname=name, creditcard=creditcard,
                            lastname=surname)
        try:
            db_conn.execute(db_registro)
        except IntegrityError as e:
            db_conn.close()
            return False

        db_conn.close()

        return True
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def db_results(searchparam=None, actit=None, genre=None):
    db_conn = None
    db_conn = db_engine.connect()
    if searchparam is None and genre is None:
        db_res = select([db_films])
        db_list = db_conn.execute(db_res)
        db_conn.close()
        return list(db_list)
    if searchparam is not None and genre is None:
        if actit == 'actdir':
            #TODO
            query = select([db_films], distinct=True).select_from(j).where(text("imdb_directors.directorname like '%{0}%' or imdb_actors.actorname like '%{1}%'".format(searchparam, searchparam)))
            result = db_conn.execute(query)
            db_conn.close()
            return list(result)
        else:
            query = select([db_films], distinct=True).where(text("imdb_movies.movietitle like '%{0}%'".format(searchparam)))
            result = db_conn.execute(query)
            db_conn.close()
            return list(result)
    if searchparam is None and genre is not None:
        j = join(db_films, db_genfilm, db_genres,
                 db_films.movieid == db_genfilm.movieid and db_genfilm.genreid == db_genres.genreid)
        query = select([db_films], distinct=True).where(text("genres.genrename like '%{0}%'".format(genre)))
        result = db_conn.execute(query)
        db_conn.close()
        return list(result)
