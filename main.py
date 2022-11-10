from flask import Flask

from maps import get_map

app = Flask(__name__)


@app.route("/")
def index():
    addresses = [
        "Ringstraße 24, 36093 Künzell",
        "Johann-Sebastian-Bach-Straße 18, 36043 Fulda",
        "Leipziger Str. 123, 36037 Fulda",
    ]
    m = get_map(addresses)
    return m._repr_html_()


if __name__ == "__main__":
    app.run(debug=True)
