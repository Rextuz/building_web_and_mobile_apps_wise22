from flask import Flask, render_template,request
import sqlite3
from maps import get_map

app = Flask(__name__)

@app.route("/home", methods=['GET', 'POST'])
def home():

    user_id = request.form["user"]
    pick_up_location = request.form["pick_up_location"]

    with sqlite3.connect("carshare.db") as con:
        cur = con.cursor()
        cur.execute("INSERT into ride_requests (user_id, pick_up_location) values (?,?)", (user_id, pick_up_location,))
        con.commit()
        msg = "Request successfully Added"

    return render_template("requests.html", msg = msg)

@app.route("/requests")
def requests():
    con = sqlite3.connect("carshare.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("select * from ride_requests")

    rows = cur.fetchall()
    for row in rows:
        print(rows)

    return render_template("requests.html", rows = rows)

@app.route("/login", methods=['GET', 'POST'])
def login():
 
    email = request.form["email"]  
    password = request.form["password"]  

    loginMsg = "Error in logging in" 
    with sqlite3.connect("carshare.db") as con:  
        cur = con.cursor()  
        cur.execute("SELECT * FROM user;")  
        rows = cur.fetchall()  

        print(rows)

        for row in rows:
            emailVal = row[2]
            passwordVal = row[3]
            print(emailVal)

            count = 0

            if emailVal == email:
                count = count + 1
            if passwordVal == password:
                count = count + 1

            if count == 2:
                idVal = row[0]
                roleVal = row[4]
                nameVal = row[1]
                loginMsg = "Logged in successfully"
                break;

    return render_template("home.html",loginMsg = loginMsg, user_id = idVal, role = roleVal, name = nameVal)

@app.route("/register", methods=['GET', 'POST'])
def register():

    name = request.form["name"]  
    email = request.form["email"]  
    password = request.form["password"]  
    role = request.form["role"]

    with sqlite3.connect("carshare.db") as con:  
        cur = con.cursor()  
        cur.execute("INSERT into user (name, email, password, role) values (?,?,?,?)",(name,email,password, role))  
        con.commit()  
        msg = "User successfully Added"  

    return render_template("index.html",msg = msg)  

def get_db_connection():
    conn = sqlite3.connect('carshare.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM user;')
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
