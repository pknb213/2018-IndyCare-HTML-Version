import os, sys
from flask import Flask, render_template, send_from_directory, send_file, Response, request, jsonify, redirect, url_for
import time, glob, json, random
import pymysql
from datetime import datetime, timedelta
from redis import Redis, RedisError
from flask_sse import sse
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from pytz import timezone

KST = timezone('Asia/Seoul')
fmtAll = '%Y-%m-%d %H:%M:%S'
fmt = '%Y-%m-%d'

# REDIS_URL = '13.209.42.91'
REDIS_URL = 'localhost'

cache = Redis(host=REDIS_URL, port=6379, db=0)
# cache = Redis(host=REDIS_URL, port=6378, db=0)
cache.flushdb()
print(cache.keys())

INTERNAL_DATABASE = False  # Todo : True is AWS, False is Internal DB

DictCursor = pymysql.cursors.DictCursor

app = Flask(__name__, template_folder=os.getcwd()+'/templates', static_folder=os.getcwd()+'/static')
app.config.update(
    DEBUG=False,
    SCREATE_KEY='secret_xxx',
    ROBOT_DATA_WAIT_TIMEOUT = 10,
    REDIS_URL="redis://%s" % REDIS_URL
)
app.register_blueprint(sse, url_prefix='/stream')

app.jinja_env.globals.update(current_user=current_user)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class Robot(UserMixin):
    def __init__(self, sn):
        self.id = sn
        self.pwd = sn


def check_robot(__id, __pwd):
    sql = "SELECT sn FROM robots WHERE sn=\"%s\" % __id"
    if MySQL.select(sql, False):
        return __id == __pwd


@login_manager.user_loader
def load_user(id):
    return Robot(id)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template("robot_list.html")
    if current_user.is_authenticated: return redirect(url_for("deployment"))
    check_robot(request.form['id'], request.form['pwd'])
    user = Robot(request.form['id'])
    login_user(user)
    return 'LOGIN'


def load_sse_command(sn, tag, __dict=None):
    if __dict is None:
        __dict = {'message': 1}
    sse.publish(__dict, channel=sn + tag)


class MySQL:
    @staticmethod
    def connect():
        if INTERNAL_DATABASE:
            db = pymysql.connect(host='13.209.42.91',
                                 port=3306,
                                 user='inventory_admin',
                                 password='nrmk2013',
                                 db='indycare',
                                 charset='utf8')
        else:
            db = pymysql.connect(host='172.23.254.121',
                                 port=3306,
                                 user='root',
                                 password='nrmk2013',
                                 db='indycare',
                                 charset='utf8')
        return db

    @classmethod
    def select(cls, __str, multi=True):
        if type(__str) is str:
            try:
                db = MySQL.connect()
                with db.cursor(DictCursor) as cursor:
                    sql = __str
                    if cursor.execute(sql):
                        if multi:
                            res = cursor.fetchall()
                            return res
                        elif not multi:
                            res = cursor.fetchone()
                            return res
                    else:
                        return False
            except Exception as e:
                print(e)
            finally:
                cursor.close()
                db.close()
        else:
            raise Exception("Please, parameter must be String !")

    @classmethod
    def insert(cls, __str):
        if type(__str) is str:
            try:
                db = MySQL.connect()
                with db.cursor(DictCursor) as cursor:
                    sql = __str
                    cursor.execute(sql)
                db.commit()
            except Exception as e:
                print(e)
            finally:
                cursor.close()
                db.close()
        else:
            raise Exception("Please, parameter must be String !")


STOP_CODE = {
    0: 'emergency stop',
    1: 'collision',
    2: 'position limit',
    3: 'velocity limit',
    4: 'motor state error',
    5: 'torque limit',
    6: 'connection lost',
    7: 'position error',
    8: 'end-tool stop',
    9: 'singular',
    10: 'over-current',
    12: 'position limit closed',
    13: 'velocity limit closed',
    14: 'singular closed',
    15: 'torque limit closed',
    61: 'computation time limit',
    62: 'control task time limit',
    90: 'reset',
    91: 'reset hard',
    94: 'reset failed',
    95: 'reset special',
    99: 'unknown'
}


def get_robot_code_description(code):
    if code in STOP_CODE:
        return STOP_CODE[code]
    return 'undefined'











