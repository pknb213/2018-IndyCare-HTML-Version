import os, sys
from flask import Flask, render_template, send_from_directory, Response, request
import time, glob
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