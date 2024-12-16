import hashlib
from tkinter.font import names

from app import db
from app.models import User, UserRole
from app import app
import cloudinary.uploader
from flask_login import current_user


def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = User.query.filter(User.username.__eq__(username.strip()),
                          User.password.__eq__(password))
    if role:
        u = u.filter(User.user_role.__eq__(role))

    return u.first()
