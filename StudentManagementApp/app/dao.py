import hashlib
from app import db
from app.models import User, UserRole, MonHoc
from app import app
import cloudinary.uploader
from flask_login import current_user




def auth_user(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()



def get_user_by_id(id):
    return User.query.get(id)

