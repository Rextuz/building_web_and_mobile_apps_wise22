from flask import Flask, render_template,request
import sqlite3
from maps import get_map

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('carshare.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/register", methods=['GET', 'POST'])
def register():

    name = request.form["name"]  
    email = request.form["email"]  
    password = request.form["password"]  
    isDriver = request.form["isDriver"]

    with sqlite3.connect("carshare.db") as con:  
        cur = con.cursor()  
        cur.execute("INSERT into user (name, email, password, isDriver) values (?,?,?,?)",(name,email,password, isDriver))  
        con.commit()  
        msg = "User successfully Added"  

    return render_template("index.html",msg = msg)  


@app.route("/")
def index():

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM ride_requests')
    rows = cur.fetchall()  
    return render_template('index.html',rows = rows)


@app.route("/map")
def map():
    addresses = [
        "Ringstraße 24, 36093 Künzell",
        "Johann-Sebastian-Bach-Straße 18, 36043 Fulda",
        "Leipziger Str. 123, 36037 Fulda",
    ]
    m = get_map(addresses)
    return m._repr_html_()


if __name__ == "__main__":
    app.run(debug=True)
