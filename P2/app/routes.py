#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session
import json
import os
import sys
import hashlib

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
    if 'usuario' in session:
        return render_template('detalle.html', movie=movies[0], sesion=session['usuario'])
    else:
        return render_template('detalle.html', movie=movies[0])

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'GET':
        return render_template('registro.html')
    elif request.method == 'POST':
        if request.form['contrasena'] == '':
            return render_template('registro.html', errorvacio=True)
        if request.form['nombre'] == '':
            return render_template('registro.html', errorvacio=True)
        if request.form['apellido'] == '':
            return render_template('registro.html', errorvacio=True)
        if request.form['email'] == '':
            return render_template('registro.html', errorvacio=True)
        if request.form['tarjeta'] == '':
            return render_template('registro.html', errorvacio=True)
        if request.form['fechanacimiento'] == '':
            return render_template('registro.html', errorvacio=True)
        if request.form['contrasena'] != request.form['contrasenaconf']:
            return render_template('registro.html', errorcont=True)
        if os.path.isdir(os.path.join(app.root_path, 'usuarios/'+request.form['email'])):
            return render_template('registro.html', errorex=True)
        os.mkdir(os.path.join(app.root_path, 'usuarios/'+request.form['email']))
        os.mknod(os.path.join(app.root_path, 'usuarios/'+request.form['email']+'/datos.json'))
        os.mknod(os.path.join(app.root_path, 'usuarios/'+request.form['email']+'/historial.json'))
        historial = {
            "peliculas": []
        }
        datos = {
            "nombre": request.form['nombre'],
            "apellido": request.form['apellido'],
            "email": request.form['email'],
            "tarjeta": request.form['tarjeta'],
            "fechanacimiento": request.form['fechanacimiento'],
            "contrasena": hashlib.md5(request.form['contrasena'].encode()).hexdigest()
        }
        with open(os.path.join(app.root_path, 'usuarios/'+request.form['email']+'/datos.json'), 'w') as datos_file:
            json.dump(datos, datos_file)
        datos_file.close()
        with open(os.path.join(app.root_path, 'usuarios/'+request.form['email']+'/historial.json'), 'w') as historial_file:
            json.dump(historial, historial_file)
        historial_file.close()

        session['usuario'] = request.form['nombre']
        session['id'] = request.form['email']
        session.modified=True

        return redirect(url_for('index'))
