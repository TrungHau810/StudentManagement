import hashlib
from app import db
from app.models import User, UserRole, MonHoc, HocSinh, BangDiem, ChiTietDiem


def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    user = User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password))
    return user.first()


def get_user_by_id(id):
    return User.query.get(id)


def add_stu_to_score():
    students = HocSinh.query.all()
    for stu in students:
        existing_scoreboard = BangDiem.query.filter_by(id_hoc_sinh=stu.id).first()
        if not existing_scoreboard:
            bang_diem = BangDiem(id_hoc_sinh=stu.id)
            db.session.add(bang_diem)

    db.session.commit()
