import hashlib
import unidecode
from flask.cli import with_appcontext

from app import db
from app.models import User, UserRole, MonHoc, HocSinh, BangDiem, ChiTietDiem


def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    user = User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password))
    return user.first()


def get_user_by_id(id):
    return User.query.get(id)


def generate_username(hoten):
    # Xóa dấu và chuyển thành chữ thường
    hoten_khong_dau = unidecode.unidecode(hoten).lower()
    # Tách họ và tên
    parts = hoten_khong_dau.split()
    # Lấy ký tự đầu của họ và tên đệm
    initials = ''.join([part[0] for part in parts[:-1]])
    # Lấy tên
    ten = parts[-1]
    # Ghép lại thành username
    username = f"{initials}{ten}"

    return username


def add_stu(ho_ten, gioi_tinh, ngay_sinh, dia_chi, email, avatar):
    username = generate_username(ho_ten)
    password = str(hashlib.md5(username.encode('utf-8')).hexdigest())

    hs = HocSinh(ho_ten=ho_ten,
              gioi_tinh=gioi_tinh,
              ngay_sinh=ngay_sinh,
              dia_chi=dia_chi,
              email=email,
              avatar=avatar,
              username=username,
              password=password,
              user_role=UserRole.STUDENT)

    db.session.add(hs)
    db.session.commit()

