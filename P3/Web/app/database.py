import os
import sys, traceback
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text, literal_column
from sqlalchemy.sql import select, insert, join, and_, or_, not_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy import func
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
db_prod = Table('products', db_meta, autoload=True, autoload_with=db_engine)
db_genres = Table('genres', db_meta, autoload=True, autoload_with=db_engine)
db_filmgen = Table('imdb_moviegenres', db_meta, autoload=True, autoload_with=db_engine)

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
        db_res = select([db_films.c.movietitle, db_prod.c.prod_id,
                        db_prod.c.price, db_prod.c.description,
                        func.string_agg(db_dirs.c.directorname, aggregate_order_by(literal_column("'; '"), db_dirs.c.directorname))], distinct=True).where(
                        and_(
                            db_prod.c.movieid == db_films.c.movieid,
                            db_films.c.movieid == db_actfilm.c.movieid,
                            db_actfilm.c.actorid == db_acts.c.actorid,
                            db_films.c.movieid == db_dirfilm.c.movieid,
                            db_dirfilm.c.directorid == db_dirs.c.directorid)
                        ).group_by(db_prod.c.prod_id, db_films.c.movietitle, db_acts.c.actorname)
        db_list = db_conn.execute(db_res)
        db_conn.close()
        return list(db_list)
    if searchparam is not None and genre is None:
        if actit == 'actdir':
            query = select([db_films.c.movietitle, db_prod.c.prod_id,
                            db_prod.c.price, db_prod.c.description,
                            func.string_agg(db_dirs.c.directorname, aggregate_order_by(literal_column("'; '"), db_dirs.c.directorname))], distinct=True).where(
                                and_(
                                    db_prod.c.movieid == db_films.c.movieid,
                                    db_films.c.movieid == db_actfilm.c.movieid,
                                    db_actfilm.c.actorid == db_acts.c.actorid,
                                    db_films.c.movieid == db_dirfilm.c.movieid,
                                    db_dirfilm.c.directorid == db_dirs.c.directorid,
                                    or_(
                                        db_acts.c.actorname.like("%{0}%".format(searchparam)),
                                        db_dirs.c.directorname.like("%{0}%".format(searchparam))
                                    )
                                )
                            ).group_by(db_prod.c.prod_id, db_films.c.movietitle, db_acts.c.actorname)
            result = db_conn.execute(query)
            db_conn.close()
            return list(result)
        else:
            query = select([db_films.c.movietitle, db_prod.c.prod_id,
                            db_prod.c.price, db_prod.c.description,
                            func.string_agg(db_dirs.c.directorname, aggregate_order_by(literal_column("'; '"), db_dirs.c.directorname))], distinct=True).where(
                                and_(
                                    db_prod.c.movieid == db_films.c.movieid,
                                    db_films.c.movieid == db_actfilm.c.movieid,
                                    db_actfilm.c.actorid == db_acts.c.actorid,
                                    db_films.c.movieid == db_dirfilm.c.movieid,
                                    db_dirfilm.c.directorid == db_dirs.c.directorid,
                                    db_films.c.movietitle.like("%{0}%".format(searchparam))
                                )
                            ).group_by(db_prod.c.prod_id, db_films.c.movietitle, db_acts.c.actorname)
            result = db_conn.execute(query)
            db_conn.close()
            return list(result)
    if searchparam is None and genre is not None:
        query = select([db_films.c.movietitle, db_prod.c.prod_id,
                        db_prod.c.price, db_prod.c.description,
                        func.string_agg(db_dirs.c.directorname, aggregate_order_by(literal_column("'; '"), db_dirs.c.directorname))], distinct=True).where(
                            and_(
                                db_prod.c.movieid == db_films.c.movieid,
                                db_films.c.movieid == db_actfilm.c.movieid,
                                db_actfilm.c.actorid == db_acts.c.actorid,
                                db_films.c.movieid == db_dirfilm.c.movieid,
                                db_dirfilm.c.directorid == db_dirs.c.directorid,
                                db_films.c.movieid == db_filmgen.c.movieid,
                                db_filmgen.c.genreid == db_genres.c.genreid,
                                db_genres.c.genrename.like("%{0}%".format(genre))
                            )
                        ).group_by(db_prod.c.prod_id, db_films.c.movietitle, db_acts.c.actorname)
        result = db_conn.execute(query)
        db_conn.close()
        return list(result)
    else:
        if actit == 'actdir':
            query = select([db_films.c.movietitle, db_prod.c.prod_id,
                            db_prod.c.price, db_prod.c.description,
                            func.string_agg(db_dirs.c.directorname, aggregate_order_by(literal_column("'; '"), db_dirs.c.directorname))], distinct=True).where(
                                and_(
                                    db_prod.c.movieid == db_films.c.movieid,
                                    db_films.c.movieid == db_actfilm.c.movieid,
                                    db_actfilm.c.actorid == db_acts.c.actorid,
                                    db_films.c.movieid == db_dirfilm.c.movieid,
                                    db_dirfilm.c.directorid == db_dirs.c.directorid,
                                    db_films.c.movieid == db_filmgen.c.movieid,
                                    db_filmgen.c.genreid == db_genres.c.genreid,
                                    db_genres.c.genrename.like("%{0}%".format(genre)),
                                    or_(
                                        db_acts.c.actorname.like("%{0}%".format(searchparam)),
                                        db_dirs.c.directorname.like("%{0}%".format(searchparam))
                                    )
                                )
                            ).group_by(db_prod.c.prod_id, db_films.c.movietitle, db_acts.c.actorname)
            result = db_conn.execute(query)
            db_conn.close()
            return list(result)
        else:
            query = select([db_films.c.movietitle, db_prod.c.prod_id,
                            db_prod.c.price, db_prod.c.description,
                            func.string_agg(db_dirs.c.directorname, aggregate_order_by(literal_column("'; '"), db_dirs.c.directorname))], distinct=True).where(
                                and_(
                                    db_prod.c.movieid == db_films.c.movieid,
                                    db_films.c.movieid == db_actfilm.c.movieid,
                                    db_actfilm.c.actorid == db_acts.c.actorid,
                                    db_films.c.movieid == db_dirfilm.c.movieid,
                                    db_dirfilm.c.directorid == db_dirs.c.directorid,
                                    db_films.c.movietitle.like("%{0}%".format(searchparam)),
                                    db_films.c.movieid == db_filmgen.c.movieid,
                                    db_filmgen.c.genreid == db_genres.c.genreid,
                                    db_genres.c.genrename.like("%{0}%".format(genre))
                                )
                            ).group_by(db_prod.c.prod_id, db_films.c.movietitle, db_acts.c.actorname)
            result = db_conn.execute(query)
            db_conn.close()
            return list(result)

def db_detail(prodid):
    db_conn = None
    db_conn = db_engine.connect()
    query1 = select([db_films.c.movietitle, db_prod.c.prod_id,
                    db_prod.c.price, db_prod.c.description,
                    func.string_agg(db_acts.c.actorname, aggregate_order_by(literal_column("'; '"), db_acts.c.actorname))], distinct=True).where(
                        and_(
                            db_films.c.movieid == db_prod.c.movieid,
                            db_prod.c.prod_id == prodid,
                            db_actfilm.c.actorid == db_acts.c.actorid,
                            db_actfilm.c.movieid == db_films.c.movieid
                            )
                        ).group_by(db_films.c.movietitle, db_prod.c.prod_id)
    result1 = db_conn.execute(query1)
    query2 = select([func.string_agg(db_genres.c.genrename, aggregate_order_by(literal_column("', '"), db_genres.c.genrename))], distinct=True).where(
                    and_(db_prod.c.prod_id == prodid,
                    db_filmgen.c.movieid == db_prod.c.movieid,
                    db_genres.c.genreid == db_filmgen.c.genreid)
                ).group_by(db_prod.c.prod_id)
    result2 = db_conn.execute(query2)
    query3 = select([func.string_agg(db_dirs.c.directorname, aggregate_order_by(literal_column("'; '"), db_dirs.c.directorname))], distinct=True).where(
                    and_(db_prod.c.prod_id == prodid,
                    db_dirfilm.c.movieid == db_prod.c.movieid,
                    db_dirs.c.directorid == db_dirfilm.c.directorid)
                ).group_by(db_prod.c.prod_id)
    result3 = db_conn.execute(query3)
    result1 = list(result1)
    result1 = list(result1[0])
    result2 = list(result2)
    result3 = list(result3)
    result1.append(result2[0][0])
    result1.insert(4, result3[0][0])
    db_conn.close()
    return result1
