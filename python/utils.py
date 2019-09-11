import os, sys
from flask import Flask, render_template, send_from_directory, Response
import time
from datetime import datetime
from redis import Redis, RedisError


app = Flask(__name__, template_folder=os.getcwd()+'/templates', static_folder=os.getcwd()+'/static')
app.config.update(
    DEBUG=False,
    SCREATE_KEY='secret_xxx',
    ROBOT_DATA_WAIT_TIMEOUT = 10
)

cache = Redis("localhost")
cache.flushdb()
print(cache.keys())
print(cache.hkeys('D11924I07T02'))
print(cache.hgetall('D11924I07T02'))
