import os
import random
import sqlite3

from names import get_full_name

DB = "carshare.db"

DRIVER_PICK_UP_LOCATIONS = [
    "Kreuzbergstraße 1, 36160 Dipperz",
    "Anton-Schmitt-Straße 27, 36039 Fulda",
    "Edelzeller Str. 13A, 36093 Künzell",
    "Steinbockstraße 13A, 36041 Fulda",
    "Iltisweg 51, 36041 Fulda",
]
PASSENGER_PICK_UP_LOCATIONS = [
    "Fulda ZOB",
    "Elchstraße 10, 36041 Fulda",
    "Bernhardstraße 10, 36043 Fulda",
    "Innstraße 5, 36043 Fulda",
    "Wiesenmühlenstraße 10, 36037 Fulda",
    "Maglianastraße 17, 36037 Fulda",
    "Lichtweg 3, 36039 Fulda",
    "Adalbertstraße 3, 36039 Fulda",
    "Am Bildstock 14, 36100 Petersberg",
    "Im Wolfsgarten 7, 36100 Petersberg",
    "Am Neuen Garten 13, 36100 Petersberg",
    "Eduard-Stieler-Ring 2, 36100 Petersberg",
    "Robert-Kronfeld-Straße 21, 36041 Fulda",
    "Emil-Nolde-Allee 24, 36041 Fulda",
    "Otto-Lilienthal-Straße 27, 36041 Fulda",
    "Nikolausstraße 18, 36037 Fulda",
    "Sturmiusstraße 9, 36037 Fulda",
    "Heinrich-von-Bibra-Platz 1a, 36037 Fulda",
    "Lindenstraße 6A, 36037 Fulda",
]


def _add_user(name, role):
    email = name.lower().replace(" ", ".") + "@example.com"
    password = "password"
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute(
            "INSERT into user (name, email, password, role) values (?,?,?,?)",
            (name, email, password, role),
        )


def add_ride_requests():
    with sqlite3.connect(DB) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM user;")
        rows = cur.fetchall()
        rows = [dict(row) for row in rows]

    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        for user in rows:
            address_list = DRIVER_PICK_UP_LOCATIONS if user["role"] == "DRIVER" else PASSENGER_PICK_UP_LOCATIONS
            random.shuffle(address_list)
            cur.execute(
                "INSERT into ride_requests (user_id, pick_up_location) values (?,?)",
                (user["id"], address_list.pop()),
            )


def add_users():
    for _ in range(5):
        _add_user(get_full_name(), "DRIVER")
    for _ in range(15):
        _add_user(get_full_name(), "PASSENGER")


if __name__ == "__main__":
    try:
        os.unlink(DB)
    except FileNotFoundError:
        pass
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute(""" CREATE TABLE IF NOT EXISTS user (
                                        id integer PRIMARY KEY,
                                        name text,
                                        email text,
                                        password text,
                                        role text
                                    ); """)
        cur.execute("""CREATE TABLE IF NOT EXISTS ride_requests (
                                    id integer PRIMARY KEY,
                                    user_id integer NOT NULL,
                                    pick_up_location text NOT NULL,
                                    FOREIGN KEY (user_id) REFERENCES user (id)
                                );""")
    add_users()
    add_ride_requests()
