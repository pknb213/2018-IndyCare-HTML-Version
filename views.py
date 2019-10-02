from utils import *


@app.route('/deployment/<sn>')
def deployment(sn):
    return render_template("videio.html", sn=sn)


@app.route("/")
def home():
    # if not current_user.is_authenticated: return redirect(url_for('login'))
    return render_template("robot_list.html")


@app.route("/display", methods=["GET"])
def test():
    # print(request.args)
    return render_template("display.html")




