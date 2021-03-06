from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import configparser

config = configparser.ConfigParser()
config_file = config.read("config.ini")[0]

app = Flask(__name__)
app.secret_key = "bn94127hf921hf9312h932qe9ufhqe90fh028r18923"
db_string = "mysql+pymysql://{}:{}@{}/{}".format(
    config["mysql"]["user"],
    config["mysql"]["password"],
    config["mysql"]["ip"],
    config["mysql"]["db"]
)
app.config['SQLALCHEMY_DATABASE_URI'] = db_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.static_folder = 'static'
db = SQLAlchemy(app)

from app import helpers, routes, filters

