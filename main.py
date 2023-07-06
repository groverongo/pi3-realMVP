from flask import Flask, jsonify, request, render_template, request, redirect
import sqlite3

app = Flask(__name__)

insert_query = '''
    INSERT INTO publicaciones
    (latitude, longitude, aforo, horario_inicio, horario_fin, precio)
    VALUES (?, ?, ?, ?, ?, ?)
'''

# Helper function to establish a database connection
def create_connection():
    connection = sqlite3.connect('espacios.db')
    connection.row_factory = sqlite3.Row
    return connection

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
        publicacion = {
            "lat": publicacion['latitude'],
            "lng": publicacion['longitude'],
            "precio": publicacion['precio'],
            "desc": f"""Aforo: {publicacion["aforo"]}\nInicio: {publicacion["horario_inicio"]}\nFin: {publicacion["horario_fin"]}"""
        }
        publicaciones.append(publicacion)

    return jsonify(publicaciones)

@app.route('/publicar', methods=['POST'])
def create_post():
    lat = request.form.get("latitude")
    lng = request.form.get("longitude")
    aforo = request.form.get("aforo")
    inicio = request.form.get("horario_inicio")
    fin = request.form.get("horario_fin")
    precio = request.form.get("precio")
    
    # Connect to the database
    db = create_connection()
    cursor = db.cursor()
    cursor.execute(insert_query, (lat, lng, aforo, inicio, fin, precio))
    db.commit()

    return redirect("/")

@app.get("/")
def index():
    return render_template("login.html")

@app.get("/tutor")
def tutor():
    return render_template("tutor.html")

@app.get("/anfitrion")
def anfitrion():
    return render_template("anfitrion.html")

# Define a route to retrieve data from the database
@app.route('/users', methods=['GET'])
def get_users():
    # Connect to the database
    connection = create_connection()
    if connection is None:
        return jsonify({'message': 'Error connecting to the database'})

    try:
        # Execute a query to retrieve all users
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM users')
            result = cursor.fetchall()
            # Convert the result to a list of dictionaries
            users = [{'id': row[0], 'name': row[1], 'email': row[2]} for row in result]
            return jsonify(users)
    except:
        print(f"Error retrieving users:")
        return jsonify({'message': 'Error retrieving users'})
    finally:
        # Close the database connection
        connection.close()

@app.route('/login',methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('pass')

    if not email or not password:
        return jsonify({'message': 'email and password are required'})

    # Connect to the database
    connection = create_connection()
    if connection is None:
        return jsonify({'message': 'Error connecting to the database'})

    try:
        # Execute a query to insert a new user
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM USERS WHERE email = %s and password = %s', (email, password))
            connection.commit()
            result = cursor.fetchall()
            if(len(result)):
                return jsonify({'message':'Valid login'}) 
            else:
                return jsonify({'message':'Error in login'}) 
    except Error as e:
        print(f"Error login user: {e}")
        return jsonify({'message': 'Error in login'})
    finally:
        # Close the database connection
        connection.close()



# Define a route to create a new user in the database
@app.route('/users', methods=['POST'])
def create_user():
    name = request.json.get('name')
    email = request.json.get('email')
    password = request.json.get('pass')

    if not name or not email:
        return jsonify({'message': 'Name and email are required'})

    # Connect to the database
    connection = create_connection()
    if connection is None:
        return jsonify({'message': 'Error connecting to the database'})

    try:
        # Execute a query to insert a new user
        with connection.cursor() as cursor:

            cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)', (name, email,password))
            connection.commit()
            return jsonify({'message': 'User created successfully'})
    except:
        print("Error creating user:")
        return jsonify({'message': 'Error creating user'})
    finally:
        # Close the database connection
        connection.close()

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
