from flask import Flask, jsonify, request, render_template, request, redirect, make_response
import sqlite3
import base64

app = Flask(__name__)

insert_query = '''
    INSERT INTO publicaciones
    (latitude, longitude, aforo, horario_inicio, horario_fin, precio, phone, usuario, image)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

# Helper function to establish a database connection
def create_connection():
    connection = sqlite3.connect('espacios.db')
    connection.row_factory = sqlite3.Row
    return connection

def create_table():
    query = '''
        CREATE TABLE IF NOT EXISTS publicaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude DECIMAL(9, 6),
            longitude DECIMAL(9, 6),
            aforo INTEGER,
            horario_inicio TIME,
            horario_fin TIME,
            precio DECIMAL(8, 2),
            phone TEXT,
            usuario TEXT,
            image BLOB
        )
    '''
    db = create_connection()
    db.execute(query)
    db.commit()
    query = '''
        CREATE TABLE IF NOT EXISTS reservas(  
            id INTEGER NOT NULL,
            usuario TEXT NOT NULL
        )
    '''
    db.execute(query)
    db.commit()
    db.close()


create_table()

verificar_q = '''
    SELECT * 
    FROM usuarios 
    WHERE usuario = ?;
'''

@app.route("/verificar", methods=['POST'])
def verificar():
    data = request.get_json()
    db = create_connection()
    cursor  = db.cursor()
    cursor.execute(verificar_q, (data['usuario']))
    rows = cursor.fetchall()
    if len(rows) == 0:
        return "No hallado"
    return "Hallado"

@app.route('/publicaciones', methods=['GET'])
def get_publicaciones():
    query = 'SELECT * FROM publicaciones'
    db = create_connection()
    cursor = db.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    publicaciones = []
    for row in rows:
        publicacion = dict(row)
        publicacion['image'] = base64.b64encode(publicacion['image']).decode('utf-8')
        publicaciones.append(publicacion)

    return jsonify(publicaciones)

@app.delete("/eliminar/<nro>")
def eliminar(nro):
    db = create_connection()
    cursor = db.cursor()
    cursor.execute("""
        DELETE FROM publicaciones WHERE id = ?;
    """, (nro));
    db.commit()
    db.close()

@app.route('/publicar', methods=['POST'])
def create_post():
    lat = request.form.get("latitude")
    lng = request.form.get("longitude")
    aforo = request.form.get("aforo")
    inicio = request.form.get("horario_inicio")
    fin = request.form.get("horario_fin")
    precio = request.form.get("precio")
    phone = request.form.get("phone")
    usuario = request.cookies.get("usuario")
    image = request.files.get('image')
    image_data = image.read()

    
    print(usuario)
    # Connect to the database
    db = create_connection()
    cursor = db.cursor()
    cursor.execute(insert_query, (lat, lng, aforo, inicio, fin, precio, phone, usuario, image_data))
    db.commit()
    db.close()

    return redirect("/")

@app.route("/nuevapub")
def nueva_publicacion():
    return render_template("anfitrion.html")

@app.get("/")
def index():
    return render_template("login.html")

@app.get("/tutor")
def tutor():
    return render_template("tutor.html")

@app.get("/anfitrion")
def anfitrion():
    usuario = request.cookies.get("usuario")
    query = 'SELECT * FROM publicaciones WHERE usuario = ?'
    db = create_connection()
    cursor = db.cursor()
    cursor.execute(query, (usuario,))
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
