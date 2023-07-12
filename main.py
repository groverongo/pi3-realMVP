from flask import Flask, jsonify, request, render_template, request, redirect, make_response
import sqlite3
import base64

app = Flask(__name__)

# Helper function to establish a database connection
def create_connection():
    connection = sqlite3.connect('espacios.db')
    connection.row_factory = sqlite3.Row
    return connection

def create_table():
    query = '''
        CREATE TABLE IF NOT EXISTS publicaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude DECIMAL(9, 6) NOT NULL,
            longitude DECIMAL(9, 6) NOT NULL,
            aforo INTEGER NOT NULL,
            horario_inicio TIME NOT NULL,
            horario_fin TIME NOT NULL,
            precio DECIMAL(8, 2) NOT NULL,
            phone TEXT NOT NULL,
            usuario TEXT NOT NULL,
            image BLOB NOT NULL,
            direccion TEXT NOT NULL
        );
    '''
    db = create_connection()
    db.execute(query)
    db.commit()
    query = '''
        CREATE TABLE IF NOT EXISTS reservas(  
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            publicacion_id INTEGER NOT NULL,
            FOREIGN KEY(publicacion_id) REFERENCES publicaciones(id)
        );
    '''
    db.execute(query)
    db.commit()
    query = '''
        CREATE TABLE IF NOT EXISTS interesados(  
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL
        );
    '''
    db.execute(query)
    db.commit()
    db.close()


create_table()

@app.get("/")
def landing():
    return render_template("landing.html")

@app.delete("/eliminarReserva/<nro>")
def eliminar_reserva(nro):
    usuario = request.cookies.get("usuario")
    db = create_connection()
    cursor = db.cursor()
    cursor.execute("""
        DELETE FROM reservas WHERE usuario = ? AND publicacion_id = ? ;
    """, (usuario,nro));
    db.commit()
    db.close()
    return "Eliminado"

@app.post("/nuevareserva/<nro>")
def nueva_reserva(nro):
    usuario = request.cookies.get("usuario")
    db = create_connection()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO reservas
        (usuario, publicacion_id)
        VALUES (?, ?);
    ''', (usuario, int(nro)))
    db.commit()
    db.close()
    return ""

@app.get("/reservas")
def ver_reservas():
    usuario = request.cookies.get("usuario")
    reservas = []
    db = create_connection()
    cursor = db.cursor()
    cursor.execute("""
        SELECT * 
        FROM publicaciones
        WHERE id in (
            SELECT publicacion_id 
            FROM reservas 
            WHERE usuario = ? 
        );
    """, (usuario,))
    rows = cursor.fetchall()
    for row in rows:
        reserva = dict(row)
        reserva['image'] = base64.b64encode(reserva['image']).decode('utf-8')
        reservas.append(reserva)
    cursor.close()
    db.close()
    return render_template("reservas.html", data=reservas)

@app.route('/publicaciones', methods=['GET'])
def get_publicaciones():
    db = create_connection()
    cursor = db.cursor()
    cursor.execute('''
        SELECT * 
        FROM publicaciones;
    ''')
    rows = cursor.fetchall()

    publicaciones = []
    for row in rows:
        publicacion = dict(row)
        publicacion['image'] = base64.b64encode(publicacion['image']).decode('utf-8')
        publicaciones.append(publicacion)

    return jsonify(publicaciones)

@app.delete("/eliminarPublicacion/<nro>")
def eliminar(nro):
    db = create_connection()
    cursor = db.cursor()
    cursor.execute("""
        DELETE FROM publicaciones 
        WHERE id = ?;
    """, (nro,));
    db.commit()
    db.close()
    return "Eliminado"

@app.get("/interesados/<nro>")
def interesados(nro):
    db = create_connection()
    cursor = db.cursor()
    cursor.execute('''
        SELECT usuario 
        FROM reservas
        WHERE publicacion_id = ?;
    ''', (nro, ))
    rows = cursor.fetchall()

    publicaciones = []
    for row in rows:
        publicacion = dict(row)
        publicaciones.append(publicacion)

    print(publicaciones)

    return jsonify(publicaciones)

@app.post("/interes")
def interes():
    correo = request.form.get("correo")
    db = create_connection()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO interesados (usuario)
        VALUES (?);
    """, (correo,));
    db.commit()
    return redirect("/login")

@app.route('/publicar', methods=['POST'])
def create_post():
    lat = request.form.get("latitude")
    lng = request.form.get("longitude")
    aforo = request.form.get("aforo")
    inicio = request.form.get("horario_inicio")
    fin = request.form.get("horario_fin")
    precio = request.form.get("precio")
    phone = request.form.get("phone")
    direccion = request.form.get("direccion")
    usuario = request.cookies.get("usuario")
    image = request.files.get('image')
    image_data = image.read()

    db = create_connection()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO publicaciones
        (latitude, longitude, aforo, horario_inicio, horario_fin, precio, phone, usuario, image, direccion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (lat, lng, aforo, inicio, fin, precio, phone, usuario, image_data, direccion))
    db.commit()
    db.close()

    return redirect("/anfitrion")

@app.route("/nuevapub")
def nueva_publicacion():
    return render_template("anfitrion.html")

@app.get("/login")
def index():
    return render_template("login.html")

@app.get("/tutor")
def tutor():
    return render_template("tutor.html")

@app.get("/anfitrion")
def anfitrion():
    usuario = request.cookies.get("usuario")
    db = create_connection()
    cursor = db.cursor()
    cursor.execute("""
        SELECT * 
        FROM publicaciones 
        WHERE usuario = ?;
    """, (usuario,))
    rows = cursor.fetchall()
    db.close()

    print(usuario)

    publicaciones = []
    for row in rows:
        publicacion = dict(row)
        publicacion['image'] = base64.b64encode(publicacion['image']).decode('utf-8')
        publicaciones.append(publicacion)

    return render_template("espacios.html", data=publicaciones)

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
