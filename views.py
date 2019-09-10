from utils import *


@app.route('/')
def home():
    return render_template("videio.html")

