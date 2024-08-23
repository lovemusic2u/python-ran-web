from flask import Flask, render_template
from shop import *
from point import *
from time_point import *

app = Flask(__name__)

app.register_blueprint(shop)
app.register_blueprint(point)
app.register_blueprint(time_point)

app.secret_key = ""

@app.route("/")
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
