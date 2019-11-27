#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from app import database
from flask import render_template, request, url_for, redirect, session, make_response, flash
import json
import os
import sys
import hashlib
import random
from datetime import date


@app.route('/')
@app.route('/index')
def index():
    init_year = 2017
    catalogue = database.db_get_top_ventas(2017)
    return render_template('index.html', title = "Home", movies=catalogue)


@app.route('/login', methods=['GET', 'POST'])
def login():
    usuario = None
    if 'usuario' in request.cookies:
        usuario = request.cookies['usuario']
    if request.method == 'GET':
        return render_template('login.html', usuario=usuario)
    elif request.method == 'POST':
        if request.form['contrasena'] == '':
            return render_template('login.html', errorvacio=True, usuario=usuario)
        if request.form['email'] == '':
            return render_template('login.html', errorvacio=True, usuario=usuario)
        matches = database.db_login(request.form['email'], request.form['contrasena'])
        if len(matches) > 0:
            session['usuario'] = matches[0]['firstname']
            session['id'] = matches[0]['customerid']
            session['email'] = matches[0]['email']
            if not 'carrito' in session:
                session['carrito'] = {}
            session['carrito'] = database.db_merge_order(session['id'], session['carrito'])
            print(session['carrito'])
            session['orderid'] = database.db_get_order(session['id'])
            session.modified = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', errorpass=True, usuario=usuario)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    response = make_response(redirect(url_for('index')))
    response.set_cookie('usuario', session['email'])
    session.pop('usuario', None)
    session.pop('carrito', None)
    session.modified = True
    return response


@app.route('/iframes/<name>')
def iframes(name):
    if 'usuario' in session:
        return render_template(name, sesion=session['usuario'])
    else:
        return render_template(name)


@app.route('/resultados')
def resultados():
    params = request.args
    if params['searchparam'] == "" and params['genero'] == 'cualquiera':
        movies = database.db_results()
    elif params['searchparam'] != "" and params['genero'] == 'cualquiera':
        movies = database.db_results(params['searchparam'], params['textchoice'])
    elif params['searchparam'] == "" and params['genero'] != 'cualquiera':
        movies = database.db_results(genre=params['genero'])
    else:
        movies = database.db_results(params['searchparam'], params['textchoice'], params['genero'])
    return render_template('resultados.html', movies=movies)


@app.route('/detalle/<id>', methods=['GET', 'POST'])
def detalle(id):
    id = int(id)
    movie = database.db_detail(id)
    if request.method == 'POST':
        print(session)
        if 'anadir' in request.form:
            if id in session['carrito']:
                if database.db_get_stock(id) <= session['carrito'][id]:
                    if len(movie[5]) > 1024:
                        movie[5] = movie[5][:1023]
                        movie[5] += "..."
                    return render_template('detalle.html', movie=movie, added=False, stock=True)
            elif database.db_get_stock(id) == 0:
                return render_template('detalle.html', movie=movie, added=False, stock=True)
            if 'carrito' not in session:
                session['carrito'] = {}
            if 'usuario' in session:
                database.db_insert_product(id, session['orderid'], 1)
            if id in session['carrito']:
                session['carrito'][id] = session['carrito'][id] + 1
            else:
                session['carrito'][id] = 1
            session.modified = True
            added = True
        else:
            added = False
    else:
        added = False
    if len(movie[5]) > 1024:
        movie[5] = movie[5][:1023]
        movie[5] += "..."
    return render_template('detalle.html', movie=movie, added=added, stock=False)


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'GET':
        return render_template('registro.html')
    elif request.method == 'POST':

        s = request.form
        valid = database.db_registro(s['email'], s['contrasena'], s['genero'],
                             s['nombre'], s['tarjeta'], s['apellido'])
        if(valid == False):
            return render_template('registro.html', errorex=True)

        matches = database.db_login(s['email'], s['contrasena'])
        session['usuario'] = matches[0]['firstname']
        session['id'] = matches[0]['customerid']
        session['email'] = matches[0]['email']
        session['carrito'] = {}
        session['orderid'] = database.db_create_order(session['id'])[0][0]
        session.modified=True

        return redirect(url_for('index'))


@app.route('/carrito', methods=['GET', 'POST'])
def carrito():
    #Cálculos generales
    suma = 0
    carr = []
    if 'carrito' not in session:
        session['carrito'] = {}
        session.modified = True
    for id in session['carrito']:
        id = int(id)
        data = database.db_detail(id)
        data.append(session['carrito'][id])
        carr.append(data)
        #Si el usuario no está loggeado, no tenemos NI IDEA de cuál es el impuesto a aplicar, luego 0
        suma += data[7]*data[2]

    if 'usuario' in session:
        suma = database.db_get_totalamount(session['orderid'])


    #Renderización inicial
    if request.method == 'GET':
        return render_template('carrito.html', carr=carr, suma=round(suma,2))

    #POST (Compra o modificación de carrito)
    if request.method == 'POST':
        if 'idAdd' in request.form:
            id = request.form['idAdd']
            id = int(id)
            if database.db_get_stock(id) <= session['carrito'][id]:
                return render_template('carrito.html', carr=carr,
                                        suma=suma, msg='No hay suficiente stock de esa película')
            if 'usuario' in session:
                database.db_insert_product(id, session['orderid'], 1)
            session['carrito'][id] += 1
            session.modified = True
            return redirect(url_for('carrito'))
        if 'idRemove' in request.form:
            id = request.form['idRemove']
            id = int(id)
            print(session['carrito'])
            if session['carrito'][id]==1:
                if 'usuario' in session:
                    database.db_remove_product(id, session['orderid'])
                session['carrito'].pop(id)
                session.modified = True
            else:
                if 'usuario' in session:
                    database.db_insert_product(id, session['orderid'], -1)
                session['carrito'][id] -= 1
                session.modified = True
            return redirect(url_for('carrito'))
            #Compra
        if 'usuario' in session:
            if database.db_get_saldo(session['id']) < suma:
                return render_template('carrito.html', carr=carr, suma=suma, msg='No hay suficiente saldo')
            for item in session['carrito'].keys():
                if database.db_get_stock(item) < session['carrito'][item]:
                    return render_template('carrito.html', carr=carr, suma=suma,
                            msg=('No hay stock del producto' + db_get_movie_name(item)))
            # En cualquier otro caso, la compra se puede realizar con éxito
            # for item in session['carrito'].keys():
            #     database.db_sell_films(item, session['carrito'][item])
            database.db_user_finalizar_compra(session['id'], suma)
            database.db_order_paid(session['orderid']) #HACER FUNCION
            session['orderid'] = database.db_create_order(session['id'])[0][0]
            session['carrito'] = {}
            return render_template('carrito.html', carr=[], suma=0, msg='¡Compra realizada con éxito!')
        else:
            return render_template('carrito.html', carr=carr, suma=suma, msg='Necesitas estar logueado para poder comprar')


@app.route('/historial', methods=['GET', 'POST'])
def historial():
    if request.method == 'GET':
        if 'usuario' not in session:
            return redirect(url_for('login'))
        historial_file = open(os.path.join(app.root_path,'usuarios/'+session['id']+'/historial.json'), encoding="utf-8").read()
        historial = json.loads(historial_file)
        datos_file = open(os.path.join(app.root_path,'usuarios/'+session['id']+'/datos.json'), encoding="utf-8").read()
        datos = json.loads(datos_file)
        return render_template("historial.html", hist=historial['pedidos'], saldo=datos['saldo'])

    if request.method == 'POST':
        if 'anadir' in request.form:
            datos_file = open(os.path.join(app.root_path,'usuarios/'+session['id']+'/datos.json'), encoding="utf-8").read()
            datos = json.loads(datos_file)
            datos['saldo'] += 10
            with open(os.path.join(app.root_path, 'usuarios/'+session['id']+'/datos.json'), mode='w', encoding='utf-8') as dat_file:
                json.dump(datos, dat_file, ensure_ascii=False)
            dat_file.close()
        return redirect(url_for('historial'))


@app.route('/visitors', methods=['GET'])
def visitors():
    return "Visitantes en línea: " + str(random.randint(0,100))
