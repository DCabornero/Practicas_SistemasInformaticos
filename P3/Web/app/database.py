import os
import sys, traceback
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text, literal_column
from sqlalchemy.sql import select, insert, join, and_, or_, not_, update
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
db_orders = Table('orders', db_meta, autoload=True, autoload_with=db_engine)
db_orddet = Table('orderdetail', db_meta, autoload=True, autoload_with=db_engine)

# Función que obtiene un usuario dados su email y contraseña si este existe
# Se usa para el login
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

# Inserta un nuevo usuario en la tabla customers si no hay inconsistencias
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

# Devuelve los resultados de una búsqueda dados ciertos filtros
def db_results(searchparam=None, actit=None, genre=None):
    db_conn = None
    db_conn = db_engine.connect()
    # Si no se pone ninguna restricción
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
    # Si hay restricciones que no son el género
    if searchparam is not None and genre is None:
        # Si hay que filtrar solo por Actor/Director
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
        # Si hay que filtrar solo por Titulo
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
    # Si solo tenemos que filtrar por género
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
        # Si tenemos que buscar por género y filtrar por Actor/Director
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
        # Si tenemos que buscar por género y por Título
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

# Devuelve los detalles del producto indicado con prod_id
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

# Comprueba si existe un carrito del usuario en la base de datos
def db_check_carrito(userid):
    db_conn = None
    db_conn = db_engine.connect()
    checkquery = select([func.count()]).select_from(db_orders).where(
        and_(db_orders.c.customerid == userid,
             db_orders.c.status == None))
    check = list(db_conn.execute(checkquery))
    db_conn.close()
    if(check[0][0] == 0):
        return False
    else:
        return True

# Obtiene el stock de cierto producto
def db_get_stock(prod_id):
    db_conn = None
    db_conn = db_engine.connect()
    query = select([db_prod.c.stock]).select_from(db_prod).where(
        db_prod.c.prod_id == prod_id
    )
    result = list(db_conn.execute(query))
    db_conn.close()
    return result[0][0]

# Obtiene las ventas de cierto producto
def db_get_sales(prod_id):
    db_conn = None
    db_conn = db_engine.connect()
    query = select([db_prod.c.sales]).select_from(db_prod).where(
        db_prod.c.prod_id == prod_id
    )
    result = list(db_conn.execute(query))
    db_conn.close()
    return result[0][0]

# Crea un carrito vacío
def db_create_order(userid):
    db_conn = None
    db_conn = db_engine.connect()
    query = db_orders.insert().values(customerid=userid)
    db_conn.execute(query)
    query2 = select([db_orders.c.orderid]).where(
        and_(
            db_orders.c.customerid == userid,
            db_orders.c.status == None
        )
    )
    result = db_conn.execute(query2)
    result = list(result)
    db_conn.close()
    return result

# Obtiene el carrito del usuario (Se comprueba previamente si existe en python
# con la función db_check_carrito)
def db_get_order(userid):
    db_conn = None
    db_conn = db_engine.connect()
    checkquery = select([db_orders.c.orderid]).select_from(db_orders).where(
        and_(db_orders.c.customerid == userid,
             db_orders.c.status == None))
    check = list(db_conn.execute(checkquery))
    db_conn.close()
    return check[0][0]

# Obtiene el precio de cierto producto
def db_get_price(prod_id):
    db_conn = None
    db_conn = db_engine.connect()
    query = select([db_prod.c.price]).select_from(db_prod).where(
        db_prod.c.prod_id == prod_id
    )
    result = list(db_conn.execute(query))
    db_conn.close()
    return result[0][0]

# Obtiene la cantidad existente de un producto en el carrito del usuario
def db_get_quantity(prod_id, orderid):
    db_conn = None
    db_conn = db_engine.connect()
    query = select([db_orddet.c.quantity]).select_from(db_orddet).where(
        and_(
            db_orddet.c.prod_id == prod_id,
            db_orddet.c.orderid == orderid
    ))
    result = list(db_conn.execute(query))
    db_conn.close()
    return result[0][0]

# Inserta cierta cantidad de un producto en el carrito
def db_insert_product(prod_id, orderid, quantity):
    db_conn = None
    db_conn = db_engine.connect()
    checkquery = select([func.count()]).select_from(db_orders).where(
        and_(
            db_orddet.c.orderid == orderid,
            db_orddet.c.prod_id == prod_id
        )
    )
    check = list(db_conn.execute(checkquery))
    if(check[0][0] == 0):
        query = db_orddet.insert().values(orderid=orderid, prod_id=prod_id, quantity=quantity,
        price=db_get_price(prod_id))

    else:
        query = update(db_orddet).where(and_(
            db_orddet.c.orderid == orderid,
            db_orddet.c.prod_id == prod_id
        )).values(quantity=db_get_quantity(prod_id, orderid)+quantity)
    db_conn.execute(query)
    db_conn.close()

# Borra la entrada en orderdetail de cierto producto
def db_remove_product(prod_id, orderid):
    db_conn = None
    db_conn = db_engine.connect()
    query = db_orddet.delete().where(
        and_(
            db_orddet.c.orderid == orderid,
            db_orddet.c.prod_id == prod_id
        )
    )
    db_conn.execute(query)
    db_conn.close()

# Obtiene el diccionario representando el carrito del usuario
def db_get_carrito(orderid):
    db_conn = None
    db_conn = db_engine.connect()
    query = select([db_orddet.c.prod_id, db_orddet.c.quantity]).select_from(db_orddet).where(
        db_orddet.c.orderid == orderid
    )
    result = list(db_conn.execute(query))
    dict = {}
    for item in result:
        dict[item[0]] = item[1]
    db_conn.close()
    return dict

# Une el carrito previo al login con el que pudiera tener el usuario en la base de datos
def db_merge_order(userid, carrito):
    db_conn = None
    db_conn = db_engine.connect()
    if db_check_carrito(userid) == False:
        result = db_create_order(userid)
        orderid = result[0][0]
    else:
        orderid = db_get_order(userid)
    for item in carrito.keys():
        db_insert_product(item, orderid, carrito[item])
    return db_get_carrito(orderid)

# Obtiene el precio neto actual del carrito
def db_get_totalamount(orderid):
    db_conn = None
    db_conn = db_engine.connect()
    query = select([db_orders.c.totalamount]).select_from(db_orders).where(
        db_orders.c.orderid == orderid
    )
    result = list(db_conn.execute(query))
    db_conn.close()
    return result[0][0]

# Obtiene el título de una película dado un prod_id
def db_get_movie_name(product_id):
    db_conn = None
    db_conn = db_engine.connect()
    query = select([db_films.c.movietitle]).select_from(db_films).where(
        and_(
        db_prod.c.prod_id == product_id,
        db_films.c.movieid == db_prod.c.movieid)
    )
    result = list(db_conn.execute(query))
    db_conn.close()
    return result[0][0]

# Obtiene el saldo actual del usuario
def db_get_saldo(userid):
    db_conn = None
    db_conn = db_engine.connect()
    query = select([db_cust.c.saldo]).select_from(db_cust).where(
        db_cust.c.customerid == userid
    )
    result = list(db_conn.execute(query))
    db_conn.close()
    return result[0][0]

# Sustrae el precio de la compra del saldo del usuario
def db_user_finalizar_compra(userid, price):
    db_conn = None
    db_conn = db_engine.connect()
    query = update(db_cust).where(
        db_cust.c.customerid == userid
    ).values(saldo=db_get_saldo(userid)-price)
    db_conn.execute(query)
    db_conn.close()

# Cambia el status de un carrito a 'Paid'(El trigger se encarga del resto)
def db_order_paid(orderid):
    db_conn = None
    db_conn = db_engine.connect()
    query = update(db_orders).where(
        db_orders.c.orderid == orderid
    ).values(status='PAID')
    db_conn.execute(query)
    db_conn.close()

# Usa la función getTopVentas para obtener las tres películas más vendidas
# en los últimos 3 años para mostrarlas en la portada
def db_get_top_ventas(year):
    db_conn = None
    db_conn = db_engine.connect()
    result1 = db_conn.execute("SELECT * FROM getTopVentas({0})".format(year))
    result1 = list(result1)
    query1 = select([db_films.c.movietitle, db_prod.c.prod_id, db_films.c.year]).where(
        and_(
            db_films.c.movieid == db_prod.c.movieid,
            db_films.c.movietitle == result1[0][1]
        )
    )
    query2 = select([db_films.c.movietitle, db_prod.c.prod_id, db_films.c.year]).where(
        and_(
            db_films.c.movieid == db_prod.c.movieid,
            db_films.c.movietitle == result1[1][1]
        )
    )
    query3 = select([db_films.c.movietitle, db_prod.c.prod_id, db_films.c.year]).where(
        and_(
            db_films.c.movieid == db_prod.c.movieid,
            db_films.c.movietitle == result1[2][1]
        )
    )
    first = list(db_conn.execute(query1))
    first = first[0]
    second = list(db_conn.execute(query2))
    second = second[0]
    third = list(db_conn.execute(query3))
    third = third[0]
    db_conn.close()
    return [first, second, third]
