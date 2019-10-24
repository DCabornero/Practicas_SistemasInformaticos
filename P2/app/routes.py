#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session
import json
import os
import sys
import hashlib
import random
from datetime import date

@app.route('/')
@app.route('/index')
def index():
    print (url_for('static', filename='estilo.css'), file=sys.stderr)
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    return render_template('index.html', title = "Home", movies=catalogue['peliculas'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        if request.form['contrasena'] == '':
            return render_template('login.html', errorvacio=True)
        if request.form['email'] == '':
            return render_template('login.html', errorvacio=True)
        try:
            user_data = open(os.path.join(app.root_path, 'usuarios/'+request.form['email']+'/datos.json'), encoding="utf-8").read()
        except:
            return render_template('login.html', erroruser=True)
        user = json.loads(user_data)
        password = hashlib.md5(request.form['contrasena'].encode()).hexdigest()
        if password == user['contrasena']:
            session['usuario'] = user['nombre']
            session['id'] = user['email']
            session.modified = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', errorpass=True)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('usuario', None)
    session.pop('carrito', None)
    return redirect(url_for('index'))

@app.route('/iframes/<name>')
def iframes(name):
    if 'usuario' in session:
        return render_template(name, sesion=session['usuario'])
    else:
        return render_template(name)

@app.route('/resultados')
def resultados():
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    movies=catalogue['peliculas']
    params = request.args
    if(params['searchparam'] != ""):
        if(params['textchoice'] == 'actdir'):
            movies=list(filter(lambda film: params.get('searchparam').lower() in film['actores'].lower() or params.get('searchparam').lower() in film['director'].lower(), movies))
        elif(params['textchoice'] == 'titulo'):
            movies=list(filter(lambda film: params.get('searchparam').lower() in film['titulo'].lower(), movies))
    if(params['genero'] != 'cualquiera'):
        movies=list(filter(lambda film: params.get('genero').lower() in film['categoria'].lower(), movies))
    return render_template('resultados.html', movies=movies)

@app.route('/detalle/<id>', methods=['GET', 'POST'])
def detalle(id):
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    movies=catalogue['peliculas']
    movies=list(filter(lambda film: str(film['id']) == id, movies))
    if 'anadir' in request.args:
        if id in session['carrito']:
            session['carrito'][id] = session['carrito'][id] + 1
        else:
            session['carrito'][id] = 1
        added = True
    else:
        added = False
    return render_template('detalle.html', movie=movies[0], added=added)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'GET':
        return render_template('registro.html')
    elif request.method == 'POST':
        if os.path.isdir(os.path.join(app.root_path, 'usuarios/'+request.form['email'])):
            return render_template('registro.html', errorex=True)
        os.mkdir(os.path.join(app.root_path, 'usuarios/'+request.form['email']))
        os.mknod(os.path.join(app.root_path, 'usuarios/'+request.form['email']+'/datos.json'))
        os.mknod(os.path.join(app.root_path, 'usuarios/'+request.form['email']+'/historial.json'))
        historial = {
            "pedidos": []
        }
        datos = {
            "nombre": request.form['nombre'],
            "apellido": request.form['apellido'],
            "email": request.form['email'],
            "tarjeta": request.form['tarjeta'],
            "fechanacimiento": request.form['fechanacimiento'],
            "contrasena": hashlib.md5(request.form['contrasena'].encode()).hexdigest(),
            "saldo": random.randint(0,100)
        }
        with open(os.path.join(app.root_path, 'usuarios/'+request.form['email']+'/datos.json'), mode='w', encoding='utf-8') as datos_file:
            json.dump(datos, datos_file, ensure_ascii=False)
        datos_file.close()
        with open(os.path.join(app.root_path, 'usuarios/'+request.form['email']+'/historial.json'), mode='w', encoding='utf-8') as historial_file:
            json.dump(historial, historial_file, ensure_ascii=False)
        historial_file.close()

        session['usuario'] = request.form['nombre']
        session['id'] = request.form['email']
        session.modified=True

        return redirect(url_for('index'))

@app.route('/carrito', methods=['GET', 'POST'])
def carrito():
    #Cálculos generales
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    movies=catalogue['peliculas']
    carr = []
    suma = 0
    if not('carrito' in session):
        session['carrito'] = {}
    for id in session['carrito']:
        data = list(filter(lambda film: str(film['id']) == id, movies))[0]
        data['cantidad'] = session['carrito'][id]
        carr.append(data)
        suma += data['cantidad']*data['precio']

    #Renderización inicial
    if request.method == 'GET':
        return render_template('carrito.html', carr=carr, suma=round(suma,2))

    #Compra
    if request.method == 'POST':
        if 'idAdd' in request.form:
            id = request.form['idAdd']
            session['carrito'][id] += 1
            return redirect(url_for('carrito'))
        if 'idRemove' in request.form:
            id = request.form['idRemove']
            if session['carrito'][id]==1:
                session['carrito'].pop(id)
            else:
                session['carrito'][id] -= 1
            return redirect(url_for('carrito'))
        if 'usuario' in session:
            datos_file = open(os.path.join(app.root_path,'usuarios/'+session['id']+'/datos.json'), encoding="utf-8").read()
            datos = json.loads(datos_file)
            if(suma > datos['saldo']):
                return render_template('carrito.html', carr=carr, suma=round(suma,2), msg='No hay saldo suficiente para realizar la compra.')
            else:
                datos['saldo'] -= suma
                datos['saldo'] = round(datos['saldo'], 2)
                session['carrito'] = {}
                with open(os.path.join(app.root_path, 'usuarios/'+session['id']+'/datos.json'), mode='w', encoding='utf-8') as datos_file_output:
                    json.dump(datos, datos_file_output, ensure_ascii=False)
                datos_file_output.close()
                fecha = date.today()
                historial_file = open(os.path.join(app.root_path,'usuarios/'+session['id']+'/historial.json'), encoding="utf-8").read()
                historial = json.loads(historial_file)
                compra = {"carrito":carr, "fecha":fecha.strftime('%d/%m/%Y'), "total":suma}
                historial['pedidos'].append(compra)
                with open(os.path.join(app.root_path, 'usuarios/'+session['id']+'/historial.json'), mode='w', encoding='utf-8') as hist_file:
                    json.dump(historial, hist_file, ensure_ascii=False)
                hist_file.close()

                return render_template('carrito.html', carr=session['carrito'], suma=0, msg='¡Compra realizada con éxito!')
        else:
            return render_template('carrito.html', carr=carr, suma=suma, msg='Necesitas estar logueado para poder comprar')

@app.route('/historial', methods=['GET', 'POST'])
def historial():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    historial_file = open(os.path.join(app.root_path,'usuarios/'+session['id']+'/historial.json'), encoding="utf-8").read()
    historial = json.loads(historial_file)
    return render_template("historial.html", hist=historial['pedidos'])
