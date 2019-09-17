import os, sys
from flask import Flask, render_template, send_from_directory, Response, request
import time, glob, json
import pymysql
from datetime import datetime
from redis import Redis, RedisError
from flask_sse import sse


app = Flask(__name__, template_folder=os.getcwd()+'/templates', static_folder=os.getcwd()+'/static')
app.config.update(
    DEBUG=False,
    SCREATE_KEY='secret_xxx',
    ROBOT_DATA_WAIT_TIMEOUT = 10,
    REDIS_URL="redis://13.209.42.91"
)
app.register_blueprint(sse, url_prefix='/stream')

cache = Redis(host="13.209.42.91", port=6379, db=0)
cache.flushdb()
print(cache.keys())
print(cache.hkeys('D11924I07T02'))
print(cache.hgetall('D11924I07T02'))

INTERNAL_DATABASE = True

DictCursor = pymysql.cursors.DictCursor


def load_sse_command(sn):
    sse.publish({'message': 1}, channel=sn+'_ev')


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
                                 db='product',
                                 charset='utf8')
        return db

    @classmethod
    def mysql_select(cls, __str, multi=True):
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
                        return Response('SQL Fail', status=404)
            except Exception as e:
                print(e)
            finally:
                cursor.close()
                db.close()
        else:
            raise Exception("Please, parameter must be String !")

    @classmethod
    def mysql_insert(cls, __str):
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














