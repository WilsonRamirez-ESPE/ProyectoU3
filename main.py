from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import pymongo
from dotenv import load_dotenv
from datetime import datetime
from pymongo import MongoClient

load_dotenv()

# Tu configuración local de MongoDB
mongo_host_local = "localhost"
mongo_port_local = 27017  # Puerto mapeado en tu máquina host para MongoDB local
mongo_db = "AgenciaReclutamiento"

# Conexión a tu MongoDB local
client_local = MongoClient(f"mongodb://{mongo_host_local}:{mongo_port_local}/")
baseDatos_local = client_local[mongo_db]

app = Flask(__name__)

# Ruta y carga para documentos estáticos
@app.route('/Proyecto/templates/recursos/<path:filename>')
def serve_static(filename):
    return send_from_directory('templates/recursos', filename)

# Ruta y carga para la página de inicio
@app.route('/')
def inicio():
    return render_template('vistas/inicio.html')

# Ruta y carga para la página de candidatos
@app.route('/candidatos')
def candidatos():
    # Consulta en tu MongoDB local para obtener los candidatos
    candidatos = list(baseDatos_local.candidatos.find({}))
    
    # Consulta en MongoDB local para obtener las habilidades
    habilidades = list(baseDatos_local.habilidades.find({}))
    
    # Convertir ObjectId a string para evitar problemas de serialización y combinar datos
    for candidato in candidatos:
        candidato['_id'] = str(candidato['_id'])
        candidato['habilidades'] = [
            habilidad for habilidad in habilidades 
            if str(habilidad.get('IDCandidato')) == candidato['_id']
        ]
    
    return render_template('vistas/candidatos.html', candidatos=candidatos)

# Ruta y carga para la página de empresas
@app.route('/empresas')
def empresas():
    # Consulta en tu MongoDB local para obtener las empresas
    empresas = list(baseDatos_local.empresas.find({}))
    
    # Consulta en MongoDB local para obtener las ofertas de trabajo
    ofertas = list(baseDatos_local.ofertas_trabajo.find({}))
    
    # Convertir ObjectId a string para evitar problemas de serialización y combinar datos
    for empresa in empresas:
        empresa['_id'] = str(empresa['_id'])
        empresa['ofertas'] = [
            oferta for oferta in ofertas 
            if str(oferta.get('empresa')) == empresa['_id']
        ]
    
    return render_template('vistas/empresas.html', empresas=empresas)

# Ruta y carga para la página de entrevistas
@app.route('/entrevistas')
def entrevistas():
    # Consulta en tu MongoDB local para obtener los entrevistadores
    entrevistadores = list(baseDatos_local.entrevistador.find({}))
    
    # Consulta en MongoDB local para obtener las entrevistas
    entrevistas = list(baseDatos_local.entrevistas.find({}))
    
    # Convertir ObjectId a string para evitar problemas de serialización y combinar datos
    for entrevistador in entrevistadores:
        entrevistador['_id'] = str(entrevistador['_id'])
        entrevistador['entrevistas'] = [
            entrevista for entrevista in entrevistas 
            if str(entrevista.get('entrevistador')) == entrevistador['_id']
        ]
    
    return render_template('vistas/entrevistas.html', entrevistadores=entrevistadores)

# FUNCIONES PARA LA PÁGINA DE CANDIDATOS
# Ruta y funciones para agregar un candidato
@app.route('/agregar_candidato', methods=['POST'])
def agregar_candidato():
    candidato_id = request.form['id_candidato']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    correo = request.form['correo']
    telefono = request.form['telefono']
    nivel_estudio = request.form['nivel_estudio']
    puestos = request.form.getlist('puesto[]')
    empresas = request.form.getlist('empresa[]')
    anios_experiencia = request.form.getlist('anio_experiencia[]')

    experiencia_laboral = []
    for i in range(len(puestos)):
        experiencia = {
            "puesto": puestos[i],
            "empresa": int(empresas[i]),
            "anio_experiencia": int(anios_experiencia[i])
        }
        experiencia_laboral.append(experiencia)

    nuevo_candidato = {
        "_id": int(candidato_id),
        "nombre": nombre,
        "apellido": apellido,
        "correo": correo,
        "telefono": telefono,
        "nivel_estudio": nivel_estudio,
        "experiencia_laboral": experiencia_laboral
    }

    baseDatos_local.candidatos.insert_one(nuevo_candidato)

    return redirect(url_for('candidatos'))

# Ruta y funciones para agregar una habilidad
@app.route('/agregar_habilidad', methods=['POST'])
def agregar_habilidad():
    habilidad_id = request.form['id_habilidad']
    habilidad_nombre = request.form['habilidad_nombre']
    habilidad_descripcion = request.form['habilidad_descripcion']
    nivel_experiencia = request.form['nivel_experiencia']
    habilidad_candidato = request.form['id_candidato']

    nueva_habilidad = {
        "_id": int(habilidad_id),
        "nombre": habilidad_nombre,
        "descripcion": habilidad_descripcion,
        "nivel_experiencia": nivel_experiencia,
        "IDCandidato": int(habilidad_candidato)
    }
    # Insertar la nueva habilidad en la colección habilidades
    baseDatos_local.habilidades.insert_one(nueva_habilidad)
    return redirect(url_for('candidatos'))

# Ruta y funciones para eliminar un candidato/habilidad
@app.route('/eliminar_candidato', methods=['POST'])
def eliminar_candidato():
    candidato_id = int(request.form['id_candidatoE'])
    # Eliminar candidato por ID
    baseDatos_local.candidatos.delete_one({'_id': candidato_id})
    # Eliminar habilidades asociadas al candidato
    baseDatos_local.habilidades.delete_many({'IDCandidato': candidato_id})

    return redirect(url_for('candidatos'))

@app.route('/eliminar_habilidad', methods=['POST'])
def eliminar_habilidad():
    habilidad_id = int(request.form['id_habilidadE'])

    # Eliminar habilidad por ID
    baseDatos_local.habilidades.delete_one({'_id': habilidad_id})

    return redirect(url_for('candidatos'))

# Ruta para actualizar un candidato
@app.route('/actualizar_candidato', methods=['POST'])
def actualizar_candidato():
    id_candidato = int(request.form['id_candidato'])  # Convertir a entero si es un número entero
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    correo = request.form['correo']
    telefono = request.form['telefono']
    nivel_estudio = request.form['nivel_estudio']
    experiencia_laboral = request.form.getlist('experiencia_laboral')

    baseDatos_local.candidatos.update_one(
        {'_id': id_candidato},  # Usar directamente el entero como _id
        {'$set': {
            'nombre': nombre,
            'apellido': apellido,
            'correo': correo,
            'telefono': telefono,
            'nivel_estudio': nivel_estudio,
            'experiencia_laboral': experiencia_laboral
        }}
    )
    
    return redirect(url_for('candidatos'))

# Ruta para actualizar una habilidad
@app.route('/actualizar_habilidad', methods=['POST'])
def actualizar_habilidad():
    id_habilidad = int(request.form['id_habilidad'])  # Convertir a entero si es un número entero
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    nivel_experiencia = request.form['nivel_experiencia']
    IDCandidato = int(request.form['IDCandidato'])  # Convertir a entero si es un número entero

    baseDatos_local.habilidades.update_one(
        {'_id': id_habilidad},  # Usar directamente el entero como _id
        {'$set': {
            'nombre': nombre,
            'descripcion': descripcion,
            'nivel_experiencia': nivel_experiencia,
            'IDCandidato': IDCandidato
        }}
    )
    
    return redirect(url_for('candidatos'))

# FUNCIONES PARA LA PÁGINA DE EMPRESAS
@app.route('/agregar_empresa', methods=['POST'])
def agregar_empresa():
    empresa_id = int(request.form['id_empresa'])
    nombre = request.form['nombre']
    industria = request.form['industria']
    ubicacion = request.form['ubicacion']
    correo_contacto = request.form['correo']
    telefono_contacto = request.form['telefono']
    numero_empleados = int(request.form['numero_empleados'])
    facturacion_anual = int(request.form['facturacion_anual'])

    nueva_empresa = {
        "_id": empresa_id,
        "nombre": nombre,
        "industria": industria,
        "ubicacion": ubicacion,
        "correo_contacto": correo_contacto,
        "telefono_contacto": telefono_contacto,
        "numero_empleados": numero_empleados,
        "facturacion_anual": facturacion_anual
    }

    baseDatos_local.empresas.insert_one(nueva_empresa)
    return redirect(url_for('empresas'))

@app.route('/agregar_oferta', methods=['POST'])
def agregar_oferta():
    oferta_id = int(request.form['id_oferta'])
    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    empresa = int(request.form['empresa'])  # Asegúrate de que se refiere a un ID de empresa válido

    nueva_oferta = {
        "_id": oferta_id,
        "titulo": titulo,
        "descripcion": descripcion,
        "empresa": empresa
    }

    baseDatos_local.ofertas_trabajo.insert_one(nueva_oferta)
    return redirect(url_for('empresas'))

@app.route('/eliminar_empresa', methods=['POST'])
def eliminar_empresa():
    empresa_id = int(request.form['id_empresaE'])
    baseDatos_local.empresas.delete_one({'_id': empresa_id})
    baseDatos_local.ofertas_trabajo.delete_many({'empresa': empresa_id})
    return redirect(url_for('empresas'))

@app.route('/eliminar_oferta', methods=['POST'])
def eliminar_oferta():
    oferta_id = int(request.form['id_ofertaE'])
    baseDatos_local.ofertas_trabajo.delete_one({'_id': oferta_id})
    return redirect(url_for('empresas'))

@app.route('/actualizar_empresa', methods=['POST'])
def actualizar_empresa():
    empresa_id = int(request.form['id_empresa'])  # Convertir a entero si es un número entero
    nombre = request.form['nombre']
    industria = request.form['industria']
    ubicacion = request.form['ubicacion']
    correo_contacto = request.form['correo']
    telefono_contacto = request.form['telefono']
    numero_empleados = int(request.form['numero_empleados'])
    facturacion_anual = int(request.form['facturacion_anual'])

    baseDatos_local.empresas.update_one(
        {'_id': empresa_id},  # Usar directamente el entero como _id
        {'$set': {
            'nombre': nombre,
            'industria': industria,
            'ubicacion': ubicacion,
            'correo_contacto': correo_contacto,
            'telefono_contacto': telefono_contacto,
            'numero_empleados': numero_empleados,
            'facturacion_anual': facturacion_anual
        }}
    )
    
    return redirect(url_for('empresas'))

@app.route('/actualizar_oferta', methods=['POST'])
def actualizar_oferta():
    oferta_id = int(request.form['id_oferta'])  # Convertir a entero si es un número entero
    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    empresa = int(request.form['empresa'])  # Convertir a entero si es un número entero

    baseDatos_local.ofertas_trabajo.update_one(
        {'_id': oferta_id},  # Usar directamente el entero como _id
        {'$set': {
            'titulo': titulo,
            'descripcion': descripcion,
            'empresa': empresa
        }}
    )
    
    return redirect(url_for('empresas'))

# FUNCIONES PARA LA PÁGINA DE ENTREVISTAS
@app.route('/agregar_entrevista', methods=['POST'])
def agregar_entrevista():
    entrevista_id = int(request.form['id_entrevista'])
    candidato = int(request.form['candidato'])
    entrevistador = int(request.form['entrevistador'])
    fecha_entrevista = request.form['fecha']
    hora_entrevista = request.form['hora']

    nueva_entrevista = {
        "_id": entrevista_id,
        "candidato": candidato,
        "entrevistador": entrevistador,
        "fecha": fecha_entrevista,
        "hora": hora_entrevista
    }

    baseDatos_local.entrevistas.insert_one(nueva_entrevista)
    return redirect(url_for('entrevistas'))

@app.route('/eliminar_entrevista', methods=['POST'])
def eliminar_entrevista():
    entrevista_id = int(request.form['id_entrevistaE'])
    baseDatos_local.entrevistas.delete_one({'_id': entrevista_id})
    return redirect(url_for('entrevistas'))

@app.route('/actualizar_entrevista', methods=['POST'])
def actualizar_entrevista():
    entrevista_id = int(request.form['id_entrevista'])  # Convertir a entero si es un número entero
    candidato = int(request.form['candidato'])
    entrevistador = int(request.form['entrevistador'])
    fecha_entrevista = request.form['fecha']
    hora_entrevista = request.form['hora']

    baseDatos_local.entrevistas.update_one(
        {'_id': entrevista_id},  # Usar directamente el entero como _id
        {'$set': {
            'candidato': candidato,
            'entrevistador': entrevistador,
            'fecha': fecha_entrevista,
            'hora': hora_entrevista
        }}
    )
    
    return redirect(url_for('entrevistas'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
