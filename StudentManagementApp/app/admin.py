from tkinter.font import names

from app import db, app
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app.models import User, MonHoc, HocSinh, BangDiem, ChiTietDiem
from flask_login import current_user, logout_user
from flask_admin import BaseView, expose
from flask import redirect


admin = Admin(app, name='eCommerce Website', template_mode='bootstrap4')


