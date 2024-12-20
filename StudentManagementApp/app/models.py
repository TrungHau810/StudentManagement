import json
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime
from app import db, app
from enum import Enum as RoleEnum
import hashlib
from flask_login import UserMixin


class UserRole(RoleEnum):
    ADMIN = 1
    TEACHER = 2
    STAFF = 3
    STUDENT = 4


class Khoi(RoleEnum):
    KHOI_10 = "Khối 10"
    KHOI_11 = "Khối 11"
    KHOI_12 = "Khối 12"


class HocKy(RoleEnum):
    HK1 = "Học kỳ 1"
    HK2 = "Học kỳ 2"


class GioiTinh(RoleEnum):
    NAM = 'Nam'
    NU = 'Nữ'


class LoaiDiem(RoleEnum):
    DIEMTX = "Điểm 15 phút"
    DIEMGK = "Điểm 1 tiết"
    DIEMCK = "Điểm cuối kỳ"


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    ho_ten = Column(String(255), nullable=False)
    gioi_tinh = Column(Enum(GioiTinh), nullable=False)
    ngay_sinh = Column(DateTime, nullable=False)
    dia_chi = Column(String(255), nullable=False)
    so_dien_thoai = Column(String(15), nullable=False)
    email = Column(String(100), nullable=False)
    avatar = Column(String(255), nullable=True)
    user_role = Column(Enum(UserRole))

    def __str__(self):
        return self.ho_ten

    def get_role(self):
        return self.user_role


class GiaoVien(User):
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    he_so_luong = Column(Float, default=1.5)


class MonHoc(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_mon_hoc = Column(String(100), nullable=False)

    def __str__(self):
        return self.ten_mon_hoc


class LopHoc(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_lop = Column(String(100), nullable=False)
    si_so = Column(Integer, nullable=False)
    khoi = Column(Enum(Khoi), nullable=False)

    def __str__(self):
        return self.ten_lop


class Khoa(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_khoa = Column(String(50), nullable=False)
    hoc_ky = Column(Enum(HocKy), nullable=False)

    def __str__(self):
        return self.ten_khoa


class Diem(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    diem = Column(Float, default=0)
    lan = Column(Integer, default=1, autoincrement=True)
    loai_diem = Column(Enum(LoaiDiem), nullable=False)
    id_ket_qua_hoc_tap = relationship("KetQuaHocTap", backref='diem', lazy=True)


# class TinNhan(db.Model):
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     noi_dung = Column(String(255), nullable=False)
#     thoi_gian = Column(DateTime, default=datetime.now())
#     id_gv = Column(Integer, ForeignKey(User.id), nullable=True)
#     id_hs = Column(Integer, ForeignKey(GiaoVien.id), nullable=True)


class KetQuaHocTap(db.Model):
    id_hs = Column(Integer, ForeignKey(User.id), primary_key=True)
    id_mon_hoc = Column(Integer, ForeignKey(MonHoc.id), primary_key=True)
    id_diem = Column(Integer, ForeignKey(Diem.id), nullable=False)


class LopHocKhoa(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_lop = Column(Integer, ForeignKey(LopHoc.id), nullable=False)
    id_khoa = Column(Integer, ForeignKey(Khoa.id), nullable=False)


class HocSinhLopHocKhoa(db.Model):
    id_hs = Column(Integer, ForeignKey(User.id), primary_key=True)
    id_lop_khoa = Column(Integer, ForeignKey(LopHocKhoa.id), primary_key=True)


class GiaoVienMonHoc(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_giao_vien = Column(Integer, ForeignKey(GiaoVien.id))
    id_mon_hoc = Column(Integer, ForeignKey(MonHoc.id))


class GiaoVienMonHocLopHocKhoa(db.Model):
    id_gv_mh = Column(Integer, ForeignKey(GiaoVienMonHoc.id), primary_key=True)
    id_lop_khoa = Column(Integer, ForeignKey(LopHocKhoa.id), primary_key=True)


# Open file json
def read_json_file(json_file):
    with open(json_file, encoding='utf-8') as file:
        return json.load(file)


def load_user_to_db(json_file):
    data = read_json_file(json_file)

    for item in data:
        if item['user_role'] == "TEACHER":
            user = GiaoVien(ho_ten=item['ho_ten'],
                            username=item['username'],
                            password=str(hashlib.md5(item['password'].encode('utf-8')).hexdigest()),
                            ngay_sinh=datetime.strptime(item['ngay_sinh'], "%Y-%m-%d"),
                            dia_chi=item['dia_chi'],
                            gioi_tinh=item['gioi_tinh'],
                            so_dien_thoai=item['so_dien_thoai'],
                            email=item['email'],
                            avatar=item['avatar'],
                            user_role=item['user_role'])
        else:
            user = User(ho_ten=item['ho_ten'],
                        username=item['username'],
                        password=str(hashlib.md5(item['password'].encode('utf-8')).hexdigest()),
                        ngay_sinh=datetime.strptime(item['ngay_sinh'], "%Y-%m-%d"),
                        dia_chi=item['dia_chi'],
                        gioi_tinh=item['gioi_tinh'],
                        so_dien_thoai=item['so_dien_thoai'],
                        email=item['email'],
                        avatar=item['avatar'],
                        user_role=item['user_role'])
        db.session.add(user)
    db.session.commit()


def load_monhoc_to_db(json_file):
    data = read_json_file(json_file)

    for item in data:
        mh = MonHoc(ten_mon_hoc=item['ten_mon_hoc'])
        db.session.add(mh)
    db.session.commit()


def load_lophoc_to_db(json_file):
    data = read_json_file(json_file)

    for item in data:
        lop = LopHoc(ten_lop=item['ten_lop'],
                     si_so=item['si_so'],
                     khoi=item['khoi'])
        db.session.add(lop)
    db.session.commit()


def load_khoa_to_db(json_file):
    data = read_json_file(json_file)

    for item in data:
        khoa = Khoa(ten_khoa=item['ten_khoa'],
                    hoc_ky=item['hoc_ky'])
        db.session.add(khoa)
    db.session.commit()


def add_gv():
    list = User.query.filter(User.user_role == UserRole.TEACHER).all()
    for g in list:
        gv = GiaoVien(id=g, he_so_luong=1.5)
        db.session.add(gv)
    db.session.commit()


# def add_lop_to_khoa():
#     lop = LopHoc.query.all()
#     pass

# def add_hocsinh_to_lop():
#     hs = User.query.filter_by(user_role=UserRole.STUDENT).all()
#     lop = LopHoc.query.all()
#     for s in hs:
#         lophoc = random.choice(lop)
#         hs_lop = H(ma_hs=s.id, ma_lop=lophoc.id)
#         db.session.add(hs_lop)
#     db.session.commit()


# def add_lop_to_monhoc():
#     lop = LopHoc.query.all()
#     monhoc = MonHoc.query.all()
#
#     for l in lop:
#         for mh in monhoc:
#             lop_mon = LopHocMonHoc(ma_lop=l.id, ma_mh=mh.ma_mon_hoc)
#             db.session.add(lop_mon)
#
#     db.session.commit()
#
#
# def add_teacher_to_monhoc():
#     teachers = User.query.filter_by(user_role=UserRole.TEACHER).all()
#     monhoc = MonHoc.query.all()
#     for t in teachers:
#         mh = random.choice(monhoc)
#         teach = UserMonHoc(id_user=t.id, ma_mh=mh.ma_mon_hoc)
#         db.session.add(teach)
#     db.session.commit()
#
#
# def add_lop_to_hocky():
#     lop = LopHoc.query.all()
#     hocky = HocKy.query.all()
#     for l in lop:
#         for hk in hocky:
#             lop_hk = LopHocHocKy(id_lop=l.id, id_hoc_ky=hk.id)
#             db.session.add(lop_hk)
#     db.session.commit()
#
#
# def add_stu_to_score():
#     students = HocSinh.query.all()
#     for stu in students:
#         bd = BangDiem.query.filter_by(id_hoc_sinh=stu.id).first()
#         if not bd:
#             bang_diem = BangDiem(id_hoc_sinh=stu.id)
#             db.session.add(bang_diem)
#
#     db.session.commit()


# def add_teacher_to_monhoc():
#     teachers = User.query.filter_by(user_role=UserRole.TEACHER).all()
#     monhoc = MonHoc.query.all()
#     for t in teachers:
#         mh = random.choice(monhoc)
#         teach = UserMonHoc(id_user=t.id, ma_mh=mh.ma_mon_hoc)
#         db.session.add(teach)
#     db.session.commit()
#
#
# def add_lop_to_hocky():
#     lop = LopHoc.query.all()
#     hocky = HocKy.query.all()
#     for l in lop:
#         for hk in hocky:
#             lop_hk = LopHocHocKy(id_lop=l.id, id_hoc_ky=hk.ma_hk)
#             db.session.add(lop_hk)
#     db.session.commit()
#
#
# def add_stu_to_score():
#     students = HocSinh.query.all()
#     for stu in students:
#         bd = BangDiem.query.filter_by(id_hoc_sinh=stu.id).first()
#         if not bd:
#             bang_diem = BangDiem(id_hoc_sinh=stu.id)
#             db.session.add(bang_diem)
#
#     db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        # Tạo models cho stu_manage_db
        db.create_all()
        # Nạp data các model vào db
        load_user_to_db('data/user.json')
        load_monhoc_to_db('data/monhoc.json')
        load_lophoc_to_db('data/lophoc.json')
        load_khoa_to_db('data/khoa.json')

        # add_hocsinh_to_lop()
        # add_lop_to_monhoc()
        # add_teacher_to_monhoc()
        # add_lop_to_hocky()
        # load_loaidiem_to_db('data/loaidiem.json')