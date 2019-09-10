import os, sys
from flask import Flask, render_template, send_from_directory


app = Flask(__name__, template_folder=os.getcwd()+'/templates', static_folder=os.getcwd()+'/static')
app.config.update(
    DEBUG=False,
    SCREATE_KEY='secret_xxx',
)

