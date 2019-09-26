from utils import *


@app.route('/deployment/<sn>')
def deployment(sn):
    return render_template("videio.html", sn=sn)


@app.route("/")
def home():
    if not current_user.is_authenticated: return redirect(url_for('login'))
    return render_template("home.html")


@app.route("/test")
def test():
    return render_template("display.html", sn='D1234')




