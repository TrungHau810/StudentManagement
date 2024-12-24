from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
from flask_login import LoginManager
import cloudinary
from sqlalchemy import Integer

app = Flask(__name__)

app.secret_key = 'HGHJAHA^&^&*AJAVAHJ*^&^&*%&*^GAFGFAG'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/stu_manage_db?charset=utf8mb4" % quote("Admin@123")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

login = LoginManager(app)

cloudinary.config(
    # cloud_name="tthau2004",
    # api_key="372274126191375",
    # api_secret="Abk-RA6C6MUKDV34nOuFDhpLFjs",
    # secure=True

    #test bằng cloudinary HoangThuan
    cloud_name ="dg5ts9slf",
    api_key="523315624128241",
    api_secret="kpR83NbacJprFxwz2jCGxt3nb4E",
    secure=True
)

# sỉ số tối đa của 1 lớp
max_si_so = 40
