import hashlib
import random
import unidecode
from flask import session
from app import db, app
from app.models import (User, UserRole, Grade,
                        MonHoc, HocSinh, BangDiem, ChiTietDiem,
                        HocSinhLopHoc, LopHoc, HocKy)


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


def random_id_lop():
    x = db.session.query(LopHoc.id).all()
    y = random.choice(x)
    y_int = int(y[0])

    return y_int


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
    return hs.id


# Add học sinh vào lớp
def add_hs_to_lop(id_hs, id_lop):
    hs_lop = HocSinhLopHoc(ma_hs=id_hs, ma_lop=id_lop)
    db.session.add(hs_lop)
    db.session.commit()


def get_lophoc_by_khoi(ten_khoi):
    list_ten_lop = [lop.ten_lop for lop in LopHoc.query.filter(LopHoc.khoi == ten_khoi).all()]
    return list_ten_lop


def get_nien_khoa():
    nam_hoc_values = db.session.query( HocKy.id, HocKy.nam_hoc).all()
    # id_nam_hoc = db.session.query(HocKy.id).all()
    # a = [item[0] for item in nam_hoc_values]
    print(nam_hoc_values)
    print(type(nam_hoc_values))
    return nam_hoc_values


def get_khoi():
    return list(Grade)


def get_hs_by_lop():
    pass


if __name__ == "__main__":
    with app.app_context():
        get_nien_khoa()
