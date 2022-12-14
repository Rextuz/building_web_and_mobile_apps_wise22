import random

from flask import Flask, render_template, request
import sqlite3
from maps import get_map, sort

DB = "carshare.db"

app = Flask(__name__)


@app.route("/home", methods=["POST"])
def home():

    user_id = request.form["user"]
    pick_up_location = request.form["pick_up_location"]

    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute(
            "INSERT into ride_requests (user_id, pick_up_location) values (?,?)",
            (user_id, pick_up_location),
        )
        con.commit()
        msg = "Request successfully Added"

    return render_template("requests.html", msg=msg, rows=_get_ride_requests())


def _get_users(user_ids, role):
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            f"SELECT * FROM user"
            f" WHERE id IN ({','.join([str(user_id) for user_id in user_ids])})"
            f" AND role='{role}';"
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]


def _get_ride_requests():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT * FROM ride_requests;")

    rows = cur.fetchall()

    return [dict(row) for row in rows]


@app.route("/requests", methods=["GET"])
def requests():
    return render_template("requests.html", rows=_get_ride_requests())


@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]

    logged_in = False
    loginMsg = "Error in logging in"
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM user;")
        rows = cur.fetchall()

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
                logged_in = True
                break

    if not logged_in:
        return "No such user"

    return render_template(
        "home.html",
        loginMsg=loginMsg,
        user_id=idVal,
        role=roleVal,
        name=nameVal,
    )


@app.route("/register", methods=["POST"])
def register():

    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    role = request.form["role"]

    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute(
            "INSERT into user (name, email, password, role) values (?,?,?,?)",
            (name, email, password, role),
        )
        con.commit()
    msg = "User successfully Added"

    return render_template("index.html", msg=msg)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/plot_route")
def plot_route():
    driver = request.args.get("driver", default='', type=str)
    ride_requests = _get_ride_requests()
    active_users = set(
        [ride_request["user_id"] for ride_request in ride_requests]
    )
    drivers = _get_users(active_users, role="DRIVER")
    passengers_ids = [
        p["id"] for p in _get_users(active_users, role="PASSENGER")
    ]
    if not driver:
        your_driver = random.choice(drivers)["id"]
    else:
        your_driver = None
        for d in drivers:
            if driver.lower() in d["name"].lower():
                your_driver = d["id"]
                break
        if your_driver is None:
            return "No such driver"

    start_address = next(
        d["pick_up_location"]
        for d in ride_requests
        if d["user_id"] == your_driver
    )
    target_address = "Leipziger Str. 123, 36037 Fulda"
    waypoints = [
        ride_request["pick_up_location"]
        for ride_request in ride_requests
        if ride_request["user_id"] in passengers_ids
    ]
    addresses = [
        start_address,
        *sort(*waypoints, target=start_address)[:4],
        target_address,
    ]
    m = get_map(addresses)
    return m._repr_html_()


if __name__ == "__main__":
    app.run(debug=True)
