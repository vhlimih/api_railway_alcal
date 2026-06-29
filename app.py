from flask import Flask, request, jsonify
from flask.helpers import make_response
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin


# para subir archivos
import os
#from werkzeug.utils import secure_filename


app = Flask(__name__)

import os

app.config["MYSQL_HOST"] = os.environ.get("DB_HOST")
app.config["MYSQL_USER"] = os.environ.get("DB_USER")
app.config["MYSQL_PASSWORD"] = os.environ.get("DB_PASSWORD")
app.config["MYSQL_DB"] = os.environ.get("DB_NAME")

mysql = MySQL(app)

CORS(app)


@app.route("/nuevo_usuario", methods=["POST"])
@cross_origin()
def insertar_usuario():
    nombre = request.json["nombre"]
    apellido = request.json["apellido"]
    provincia = request.json["provincia"]

    cursor = mysql.connection.cursor()

    sql = "INSERT INTO Usuarios(nombre, apellido, provincia) values(%s, %s, %s);"
    cursor.execute(sql, (nombre, apellido, provincia))


    mysql.connection.commit()

    cursor.close()
    response = make_response()

    response = jsonify({"resultado":"Agregado nuevo usuario"})
    return response

@app.route("/traer_usuarios", methods=["GET"])
@cross_origin()
def listar_jugadores():
    #consulta SQL
    sql = "SELECT idUsuarios, nombre, apellido, provincia FROM Usuarios"

    #crear el cursor
    cursor = mysql.connection.cursor()#mysql.connect.cursor()
    cursor.execute(sql)

    resultado = cursor.fetchall()

    #cerrar la conexión
    cursor.close()
    response = make_response()

    if resultado == None:
        response = jsonify({"mensaje":None})
        return response
    else:
        usuarios = []

        for i in resultado:

            p = {"id":i[0], "nombre":i[1], "apellido":i[2], "provincia":i[3]}
            usuarios.append(p)

        return jsonify(usuarios)


@cross_origin
@app.route("/eliminar_usuario/<id>", methods=["DELETE"])
def eliminar_usuario(id):

    sql = "DELETE FROM Usuarios WHERE idUsuarios=%s"

    #crear el cursor
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (id,))

    mysql.connection.commit()

    #cerrar la conexión
    cursor.close()
    response = make_response()


    response = jsonify({"resultado":"Usuario eliminado"})
    return response


@cross_origin
@app.route("/actualizar_usuario/<id>", methods=["PUT"])
def actualizar_usuario(id):
    nombre = request.json["nom"]

    sql = "UPDATE Usuarios SET nombre=%s WHERE idUsuarios=%s"

    #crear el cursor
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (nombre, id))
    mysql.connection.commit()


    #cerrar la conexión
    cursor.close()
    response = make_response()

    response = jsonify({"resultado":"Usuario no activo"})
    return response



#########################################################################

# Proyecto

# ==============================================================================
# SECCIÓN: REGISTRO DE ASISTENCIA (NUEVO)
# ==============================================================================

# Endpoint para registrar la asistencia de un usuario en un día en particular
@app.route("/nueva_asistencia", methods=["POST"])
@cross_origin()
def insertar_asistencia():
    # Recibe el ID del usuario, la fecha (YYYY-MM-DD) y el estado (Presente/Ausente/Tarde)
    
    fecha = request.json["fecha"]
    estado = request.json["estado"]
    id_preceptor = request.json["id_preceptor"]
    id_alumno = request.json["id_alumno"]

    cursor = mysql.connection.cursor()
    
    # Query SQL para insertar los datos en la tabla Asistencias
    sql = "INSERT INTO Asistencia(fecha, estado, preceptor_idpreceptor, Alumno_idAlumno) VALUES (%s, %s, %s, %s);"
    cursor.execute(sql, (fecha, estado, id_preceptor, id_alumno))
    
    mysql.connection.commit()
    cursor.close()

    return jsonify({"resultado": "Asistencia registrada correctamente"})


# Endpoint para listar todo el historial de asistencias
@app.route("/traer_asistencias", methods=["GET"])
@cross_origin()
def listar_asistencias():
    # Usamos INNER JOIN para enlazar la tabla Asistencias con la tabla Usuarios
    # De este modo, podemos mostrar el nombre y apellido real de quien asistió
    sql = """
        SELECT a.idasistencia, a.fecha, a.estado, preceptor_idpreceptor, Alumno_idAlumno
        FROM Asistencia a
    """

    cursor = mysql.connection.cursor()
    cursor.execute(sql)
    resultado = cursor.fetchall()
    cursor.close()

    if not resultado:
        return jsonify([])
    else:
        asistencias = []
        for i in resultado:
            # Transformamos el objeto de fecha (date) proveniente de MySQL en texto string (YYYY-MM-DD)
            # para evitar que Flask falle al procesar el formato JSON.
            fecha_str = i[1].strftime('%Y-%m-%d') if hasattr(i[1], 'strftime') else str(i[1])
            
            p = {
                "id_asistencia": i[0],
                "fecha": fecha_str,
                "estado": i[2],
                "id_preceptor": i[3],
                "id_alumno":i[4]
            }
            asistencias.append(p)
            
        return jsonify(asistencias)

#######Preceptor
@app.route("/preceptor", methods=["POST"])
@cross_origin()
def insertar_preceptor():
    
    
    nombre_usuario = request.json["nombre_usuario"]
    email = request.json["email"]
    contraseña = request.json["contraseña"]

    cursor = mysql.connection.cursor()
    
    # Query SQL para insertar los datos en la tabla Asistencias
    sql = "INSERT INTO Preceptor(nombre_usuario, email, contraseña) VALUES (%s, %s, %s);"
    cursor.execute(sql, (nombre_usuario, email, contraseña))
    
    mysql.connection.commit()
    cursor.close()

    return jsonify({"resultado": "Preceptor registrado/a correctamente"})



#######alumno
@app.route("/alumno", methods=["POST"])
@cross_origin()
def insertar_preceptor():
    
    
    nombre = request.json["nombre"]
    apellido = request.json["apellido"]
    Cursos_idCursos = request.json["Cursos_idCursos"]

    cursor = mysql.connection.cursor()
    
    # Query SQL para insertar los datos en la tabla Asistencias
    sql = "INSERT INTO Preceptor(nombre, apellido, Cursos_idCursos) VALUES (%s, %s, %s);"
    cursor.execute(sql, (nombre, apellido, Cursos_idCursos))
    
    mysql.connection.commit()
    cursor.close()

    return jsonify({"resultado": "Alumno registrado/a correctamente"})















if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)