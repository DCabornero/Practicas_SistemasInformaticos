# -*- coding: utf-8 -*-

import os
import sys, traceback, time

from sqlalchemy import create_engine

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False, execution_options={"autocommit":False})

def dbConnect():
    return db_engine.connect()

def dbCloseConnect(db_conn):
    db_conn.close()

def getListaCliMes(db_conn, mes, anio, iumbral, iintervalo, use_prepare, break0, niter):

    # TODO: implementar la consulta; asignar nombre 'cc' al contador resultante
    consulta = "SELECT\
      COUNT(DISTINCT customerid) AS cc\
    FROM\
      orders\
    WHERE\
      date_part('year', orderdate) = {0} AND\
      date_part('month', orderdate) = {1} AND\
      totalamount > ".format(anio, mes)

    # TODO: ejecutar la consulta
    # - mediante PREPARE, EXECUTE, DEALLOCATE si use_prepare es True
    # - mediante db_conn.execute() si es False

    if use_prepare:
        db_conn.execute("PREPARE cons (int, int, int) AS SELECT\
          COUNT(DISTINCT customerid) AS cc\
        FROM\
          orders\
        WHERE\
          date_part('year', orderdate) = $1 AND\
          date_part('month', orderdate) = $2 AND\
          totalamount > $3;")

    # Array con resultados de la consulta para cada umbral
    dbr=[]

    for ii in range(niter):

        # TODO: ...
        if use_prepare:
            res = db_conn.execute("EXECUTE cons ({0},{1},{2});".format(anio, mes, iumbral)).first()
        else:
            consultaiter = consulta + "{0};".format(iumbral)
            res = db_conn.execute(consultaiter).first()
        # Guardar resultado de la query
        dbr.append({"umbral":iumbral,"contador":res['cc']})

        # TODO: si break0 es True, salir si contador resultante es cero
        if break0:
            if res['cc'] == 0:
                break

        # Actualizacion de umbral
        iumbral = iumbral + iintervalo

    if use_prepare:
        db_conn.execute("DEALLOCATE cons;")
    return dbr

def getMovies(anio):
    # conexion a la base de datos
    db_conn = db_engine.connect()

    query="select movietitle from imdb_movies where year = '" + anio + "'"
    resultproxy=db_conn.execute(query)

    a = []
    for rowproxy in resultproxy:
        d={}
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for tup in rowproxy.items():
            # build up the dictionary
            d[tup[0]] = tup[1]
        a.append(d)

    resultproxy.close()

    db_conn.close()

    return a

def getCustomer(username, password):
    # conexion a la base de datos
    db_conn = db_engine.connect()

    query="select * from customers where username='" + username + "' and password='" + password + "'"
    res=db_conn.execute(query).first()

    db_conn.close()

    if res is None:
        return None
    else:
        return {'firstname': res['firstname'], 'lastname': res['lastname']}

def delCustomer(customerid, bFallo, bSQL, duerme, bCommit):

    # Array de trazas a mostrar en la página
    dbr=[]
    det = "DELETE FROM orderdetail WHERE orderid IN (SELECT orderid FROM orders NATURAL JOIN customers WHERE customerid = {0})".format(customerid)
    ord = "DELETE FROM orders WHERE customerid = {0}".format(customerid)
    cust = "DELETE FROM customers WHERE customerid = {0}".format(customerid)
    detcount = "SELECT count(*) FROM orderdetail WHERE orderid IN (SELECT orderid FROM orders NATURAL JOIN customers WHERE customerid = {0})".format(customerid)
    ordcount = "SELECT count(*) FROM orders WHERE customerid = {0}".format(customerid)
    custcount = "SELECT count(*) FROM customers WHERE customerid = {0}".format(customerid)
    # TODO: Ejecutar consultas de borrado
    # - ordenar consultas según se desee provocar un error (bFallo True) o no
    # - ejecutar commit intermedio si bCommit es True
    # - usar sentencias SQL ('BEGIN', 'COMMIT', ...) si bSQL es True
    # - suspender la ejecución 'duerme' segundos en el punto adecuado para forzar deadlock
    # - ir guardando trazas mediante dbr.append()

    consultas = []
    contador = 0
    if bFallo:
        consultas.append(det)
        if bSQL and bCommit:
            consultas.append("COMMIT")
            consultas.append("BEGIN")
        consultas.append(cust)
        consultas.append(ord)
    else:
        consultas.append(det)
        if duerme and duerme > 0:
            consultas.append("sleep {0}".format(duerme))
        consultas.append(ord)
        consultas.append(cust)
    try:
        db_conn = dbConnect()
        if bSQL:
            db_conn.execute("BEGIN")
            dbr.append("Begin SQL")
        else:
            trans = db_conn.begin()
            dbr.append("Begin Alch")
        for con in consultas:
            dbr.append(con)
            if contador == 1 and bCommit and not bSQL and bFallo:
                trans.commit()
                dbr.append("Commit Alch")
                trans = db_conn.begin()
                dbr.append("Begin Alch")
            if con == "COMMIT":
                dbr.append("Commit SQL")
            elif con == "BEGIN":
                dbr.append("Begin SQL")
            elif con.split()[0] == "sleep":
                dbr.append("Sleeping")
                time.sleep(int(con.split()[1]))
                continue
            elif con.split()[2] == "orderdetail":
                dbr.append("Detalles pre-borrado:")
                dbr.append(list(db_conn.execute(detcount))[0][0])
            elif con.split()[2] == "orders":
                dbr.append("Orders pre-borrado:")
                dbr.append(list(db_conn.execute(ordcount))[0][0])
            elif con.split()[2] == "customers":
                dbr.append("Cliente pre-borrado:")
                dbr.append(list(db_conn.execute(custcount))[0][0])
            if con.split()[0] == "DELETE":
                dbr.append("Intentamos ejecutar el borrado")
            if con.split()[0] != "sleep":
                db_conn.execute(con)
            if len(con.split()) <= 2:
                continue
            if con.split()[2] == "orderdetail":
                dbr.append("Detalles post-borrado:")
                dbr.append(list(db_conn.execute(detcount))[0][0])
            elif con.split()[2] == "orders":
                dbr.append("Orders post-borrado:")
                dbr.append(list(db_conn.execute(ordcount))[0][0])
            elif con.split()[2] == "customers":
                dbr.append("Clientes post-borrado:")
                dbr.append(list(db_conn.execute(custcount))[0][0])
            contador += 1

    except Exception as e:
        if bSQL:
            db_conn.execute("ROLLBACK")
            dbr.append(str(e))
            dbr.append("Rollback SQL")
        else:
            trans.rollback()
            dbr.append(str(e))
            dbr.append("Rollback Alch")

    else:
        if bSQL:
             db_conn.execute("COMMIT")
             dbr.append("Commit SQL")
        else:
            trans.commit()
            dbr.append("Commit Alch")

    dbr.append("Estado tras ejecucion:")
    dbr.append("Details:")
    dbr.append(list(db_conn.execute(detcount))[0][0])
    dbr.append("Orders:")
    dbr.append(list(db_conn.execute(ordcount))[0][0])
    dbr.append("Customers:")
    dbr.append(list(db_conn.execute(custcount))[0][0])
    dbCloseConnect(db_conn)
    return dbr
