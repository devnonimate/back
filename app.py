from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

DATABASE = 'database.sqlite'

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = generate_password_hash(data.get('password'))

    try:
        query_db(
            'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
            (username, email, password)
        )
        return jsonify({'message': 'Usuário registrado com sucesso!'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Usuário ou e-mail já existe!'}), 409

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = query_db('SELECT * FROM users WHERE username = ?', (username,), one=True)
    if user and check_password_hash(user[3], password):
        return jsonify({'message': 'Login bem-sucedido!', 'user': {'id': user[0], 'username': user[1], 'email': user[2]}})
    return jsonify({'error': 'Credenciais inválidas!'}), 401

@app.route('/home', methods=['GET'])
def home():
    users = query_db('SELECT id, username, email FROM users')
    return jsonify({'users': [{'id': u[0], 'username': u[1], 'email': u[2]} for u in users]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
