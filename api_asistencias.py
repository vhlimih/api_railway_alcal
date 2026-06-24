from flask import Flask, request, jsonify
from flask.helpers import make_response
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__)

# ==============================================================================
# CONFIGURACIÓN DE LA BASE DE DATOS (Variables de Entorno)
# ==============================================================================
app.config["MYSQL_HOST"] = os.environ.get("DB_HOST")
app.config["MYSQL_USER"] = os.environ.get("DB_USER")
app.config["MYSQL_PASSWORD"] = os.environ.get("DB_PASSWORD")
app.config["MYSQL_DB"] = os.environ.get("DB_NAME")

mysql = MySQL(app)
CORS(app)


# ==============================================================================
# SECCIÓN: CONTROL DE USUARIOS
# ==============================================================================

# Registrar un nuevo usuario
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

    return jsonify({"resultado": "Agregado nuevo usuario"})


# Obtener todos los usuarios registrados
@app.route("/traer_usuarios", methods=["GET"])
@cross_origin()
def listar_jugadores():
    sql = "SELECT idUsuarios, nombre, apellido, provincia FROM Usuarios"
    
    cursor = mysql.connection.cursor()
    cursor.execute(sql)
    resultado = cursor.fetchall()
    cursor.close()

    if resultado is None:
        return jsonify({"mensaje": None})
    else:
        usuarios = []
        for i in resultado:
            p = {"id": i[0], "nombre": i[1], "apellido": i[2], "provincia": i[3]}
            usuarios.append(p)
        return jsonify(usuarios)


# Eliminar un usuario según su ID
@app.route("/eliminar_usuario/<id>", methods=["DELETE"])
@cross_origin()
def eliminar_usuario(id):
    sql = "DELETE FROM Usuarios WHERE idUsuarios=%s"

    cursor = mysql.connection.cursor()
    cursor.execute(sql, (id,))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"resultado": "Usuario eliminado"})


# Actualizar el nombre de un usuario según su ID
@app.route("/actualizar_usuario/<id>", methods=["PUT"])
@cross_origin()
def actualizar_usuario(id):
    nombre = request.json["nom"]

    sql = "UPDATE Usuarios SET nombre=%s WHERE idUsuarios=%s"

    cursor = mysql.connection.cursor()
    cursor.execute(sql, (nombre, id))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"resultado": "Usuario actualizado"})


# ==============================================================================
# SECCIÓN: REGISTRO DE ASISTENCIA (NUEVO)
# ==============================================================================

# Endpoint para registrar la asistencia de un usuario en un día en particular
@app.route("/nueva_asistencia", methods=["POST"])
@cross_origin()
def insertar_asistencia():
    # Recibe el ID del usuario, la fecha (YYYY-MM-DD) y el estado (Presente/Ausente/Tarde)
    id_usuario = request.json["id_usuario"]
    fecha = request.json["fecha"]
    estado = request.json["estado"]

    cursor = mysql.connection.cursor()
    
    # Query SQL para insertar los datos en la tabla Asistencias
    sql = "INSERT INTO Asistencias(id_usuario, fecha, estado) VALUES (%s, %s, %s);"
    cursor.execute(sql, (id_usuario, fecha, estado))
    
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
        SELECT a.idAsistencias, a.id_usuario, u.nombre, u.apellido, a.fecha, a.estado 
        FROM Asistencias a
        INNER JOIN Usuarios u ON a.id_usuario = u.idUsuarios
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
            fecha_str = i[4].strftime('%Y-%m-%d') if hasattr(i[4], 'strftime') else str(i[4])
            
            p = {
                "id_asistencia": i[0],
                "id_usuario": i[1],
                "nombre": i[2],
                "apellido": i[3],
                "fecha": fecha_str,
                "estado": i[5]
            }
            asistencias.append(p)
            
        return jsonify(asistencias)


# ==============================================================================
# INICIO DE LA APLICACIÓN
# ==============================================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)