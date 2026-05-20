import os
from flask import Flask, render_template
from quran.blueprint import quran_bp
from word_neighbour.blueprint import word_neighbour_bp

app = Flask(__name__)
app.register_blueprint(quran_bp)
app.register_blueprint(word_neighbour_bp)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=port)
