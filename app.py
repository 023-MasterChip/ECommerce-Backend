from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)

db = 'EComm.db'


def get_db_connection():
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def main():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                created_at DATE NOT NULL,
                role INTEGER NOT NULL
            )
        ''')

    c.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                desc TEXT NOT NULL,
                price FLOAT NOT NULL,
                image TEXT,
                category TEXT NOT NULL,
                owner INTEGER NOT NULL
            )
        ''')
    
    c.execute('''
            CREATE TABLE IF NOT EXISTS carts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cust_id TEXT NOT NULL,
                items TEXT NOT NULL
            )
        ''')

    conn.commit()
    conn.close()
    return "Table created sucessfully"


@app.route('/user/login', methods=['POST'])
def user_login():
    conn = get_db_connection()
    c = conn.cursor()

    data = request.get_json()
    username = data['username']
    password = data['password']

    c.execute("SELECT COUNT(*) FROM users WHERE username=? AND password=?",
              (username, password))
    count = c.fetchone()[0]

    if count == 1:
        return jsonify({"status": "success", "message": "login successfull"})
    else:
        return jsonify({"status": "failure", "message": "unable to login"})

@app.route('/user/signup', methods=['POST'])
def user_signup():
    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = data['password']
        date = datetime.now()

        c.execute("INSERT INTO users (username,password,created_at,role) VALUES (?,?,?,?)",
                  (username, password, date, 0))

        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "User created sucessfully"})

@app.route('/admin/<int:owner_id>', methods=['GET', 'POST'])
def admin_create_items(owner_id):
    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'GET':
        c.execute("SELECT * FROM items WHERE owner=?",(owner_id,))
        results = c.fetchall()
        items = [dict(result) for result in results]

        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "data retrieved sucessfully", "data" : items})

    if request.method == 'POST':
        data = request.get_json()
        item_name = data['name']
        description = data['description']
        price = data['price']
        category = data['category']
        img_path = data['imgsrc']
        owner = data['owner']

        c.execute("INSERT INTO items (name,desc,price,image,category,owner) VALUES (?,?,?,?,?,?)", (item_name,description,price,img_path,category,owner))

        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Item created sucessfully"})

@app.route('/admin/<int:owner_id>/item/<int:item_id>', methods=['POST', 'DELETE', 'PATCH'])
def admin_manage_items(owner_id, item_id):
    conn = get_db_connection()
    c = conn.cursor()
    if request.method == 'DELETE':
        c.execute("DELETE FROM items WHERE id = ? AND owner = ?", (item_id,owner_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Item deleted sucessfully"})

@app.route('/cust/items/', methods = ['GET'])
def view_items():
    conn = get_db_connection()
    c = conn.cursor()
    if request.method == 'GET':
        c.execute('SELECT * FROM items')
        results = c.fetchall()
        items = [dict(result) for result in results]
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "data retrieved sucessfully", "data" : items})
    
@app.route('/cust/items/<int:item_id>', methods = ['GET'])
def item(item_id):
    conn = get_db_connection()
    c = conn.cursor()
    if request.method == 'GET':
        c.execute('SELECT * FROM items where id=?',(item_id,))
        results = c.fetchall()
        items = [dict(result) for result in results]
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "data retrieved sucessfully", "data" : items})

@app.route('/cust/<int:cust_id>/cart/<int:cart_id>', methods = ['GET'])
def view_cart(cust_id, cart_id):
    pass

@app.route('/cust/item/cart/<int:cart_id>', methods=['GET', 'POST'])
def add_to_cart(item_id,cart_id):
    conn = get_db_connection()
    c=conn.cursor()
    if request.method == 'POST':
        data = request.body
        cust_id = data['cust_id']
        item_id = data['item_id']
        items = data['items']
        c.execute("INSERT INTO cart (customer_id, item_id, cart_id) VALUES (?,?,?)",(cust_id,item_id,cart_id,items))

        conn.close()
        return "item added successfully"

if __name__ == '__main__':
    app.run(debug=True)
