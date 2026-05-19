import os
from flask import Flask, render_template
from quran.blueprint import quran_bp

app = Flask(__name__)
app.register_blueprint(quran_bp)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=port)
