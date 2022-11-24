from flask import Flask, render_template
import sqlite3
from maps import get_map

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('carshare.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM user')
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
