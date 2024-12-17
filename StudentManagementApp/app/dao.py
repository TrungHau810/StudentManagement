import hashlib
from app import db
from app.models import User, UserRole, MonHoc
from app import app
import cloudinary.uploader
from flask_login import current_user


def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    user = User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password))
    # if user:
    #     user = user.filter(User.user_role.__eq__(role))

    return user.first()


def get_user_by_id(id):
    return User.query.get(id)
