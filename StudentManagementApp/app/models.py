import json
import random
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime
from app import db, app
from enum import Enum as RoleEnum
import hashlib
from flask_login import UserMixin
import cloudinary.uploader


class UserRole(RoleEnum):
    ADMIN = 1
    TEACHER = 2
    STAFF = 3


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
    avatar = Column(String(255), nullable=True)
    user_role = Column(Enum(UserRole))

    def __str__(self):
        return self.ho_ten

    def get_role(self):
        return self.user_role


class HocSinh(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ho_ten = Column(String(255), nullable=False)
    gioi_tinh = Column(Enum(GioiTinh), nullable=False)
    ngay_sinh = Column(DateTime, nullable=False)
    dia_chi = Column(String(255), nullable=False)
    so_dien_thoai = Column(String(15), nullable=False)
    email = Column(String(100), nullable=False)


    def __str__(self):
        return self.ho_ten

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


# class Diem(db.Model):
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     diem = Column(Float, default=0)
#     lan = Column(Integer, default=1, autoincrement=True)
#     loai_diem = Column(Enum(LoaiDiem), nullable=False)
#     hoc_ky = Column(Enum(HocKy), nullable=False)
#     id_ket_qua_hoc_tap = relationship("KetQuaHocTap", backref='diem', lazy=True)

class Diem(db.Model):
    __tablename__ = 'diem'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('hoc_sinh.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('mon_hoc.id'), nullable=False)
    diem = Column(Float, nullable=False)
    lan = Column(Integer, nullable=False, default=1)
    loai_diem = Column(Enum(LoaiDiem), nullable=False)
    hoc_ky = Column(Enum(HocKy), nullable=False)

    # Relationships với eager loading
    student = relationship('HocSinh', backref='diem_set', lazy='joined')
    subject = relationship('MonHoc', backref='diem_set', lazy='joined')

    def __str__(self):
        return f"{self.student.ho_ten if self.student else ''} - {self.subject.ten_mon_hoc if self.subject else ''} - {self.diem}"

# class Diem(db.Model):
#     __tablename__ = 'diem'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     student_id = Column(Integer, ForeignKey('hoc_sinh.id'), nullable=False)
#     subject_id = Column(Integer, ForeignKey('mon_hoc.id'), nullable=False)
#     diem = Column(Float, nullable=False)
#     lan = Column(Integer, nullable=False, default=1)
#     loai_diem = Column(Enum(LoaiDiem), nullable=False)
#     hoc_ky = Column(Enum(HocKy), nullable=False)
#
#
#     def __str__(self):
#         return str(self.diem)

class QuyDinh(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_quy_dinh = Column(String(255), nullable=False)
    gia_tri = Column(Integer, nullable=False)


class KetQuaHocTap(db.Model):
    id_hs = Column(Integer, ForeignKey(HocSinh.id), primary_key=True)
    id_mon_hoc = Column(Integer, ForeignKey(MonHoc.id), primary_key=True)
    id_diem = Column(Integer, ForeignKey(Diem.id), nullable=False)


class LopHocKhoa(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_lop = Column(Integer, ForeignKey(LopHoc.id), nullable=False)
    id_khoa = Column(Integer, ForeignKey(Khoa.id), nullable=False)


class HocSinhLopHocKhoa(db.Model):
    id_hs = Column(Integer, ForeignKey(HocSinh.id), primary_key=True)
    id_lop_khoa = Column(Integer, ForeignKey(LopHocKhoa.id), primary_key=True)


class GiaoVienMonHoc(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_giao_vien = Column(Integer, ForeignKey(User.id))
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
        user = User(username=item['username'],
                    password=str(hashlib.md5(item['password'].encode('utf-8')).hexdigest()),
                    avatar=item['avatar'],
                    user_role=item['user_role'])
        db.session.add(user)
    db.session.commit()


def load_hs_to_db(json_file):
    data = read_json_file(json_file)
    for item in data:
        user = HocSinh(ho_ten=item['ho_ten'],
                       gioi_tinh=item['gioi_tinh'],
                       ngay_sinh=datetime.strptime(item['ngay_sinh'], "%Y-%m-%d"),
                       dia_chi=item['dia_chi'],
                       so_dien_thoai=item['so_dien_thoai'],
                       email=item['email'])
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


def load_quy_dinh_to_db(json_file):
    data = read_json_file(json_file)
    for item in data:
        qd = QuyDinh(ten_quy_dinh=item['ten_quy_dinh'],
                     gia_tri=item['gia_tri'])
        db.session.add(qd)
    db.session.commit()


def add_lop_to_khoa():
    lop_ids = db.session.query(LopHoc.id).all()
    khoa_ids = db.session.query(Khoa.id).filter(Khoa.hoc_ky == HocKy.HK1).all()
    lop_ids = [lop[0] for lop in lop_ids]
    khoa_ids = [khoa[0] for khoa in khoa_ids]
    for lop_id in lop_ids:
        for khoa_id in khoa_ids:
            lop_hoc_khoa = LopHocKhoa(id_lop=lop_id, id_khoa=khoa_id)
            db.session.add(lop_hoc_khoa)
    db.session.commit()



def add_hocsinh_to_lopkhoa():
    hoc_sinh_ids = db.session.query(HocSinh.id).all()
    lop_khoa_ids = db.session.query(LopHocKhoa.id).all()

    hoc_sinh_ids = [hs[0] for hs in hoc_sinh_ids]
    lop_khoa_ids = [lk[0] for lk in lop_khoa_ids]

    for hs_id in hoc_sinh_ids:
        lop_khoa_id = random.choice(lop_khoa_ids)
        hs_lop_khoa = HocSinhLopHocKhoa(id_hs=hs_id, id_lop_khoa=lop_khoa_id)
        db.session.add(hs_lop_khoa)
    db.session.commit()


import random


def add_hs_to_lopkhoa():
    hoc_sinh_ids = db.session.query(HocSinh.id).all()
    lopkhoa_ids = db.session.query(LopHocKhoa.id).all()

    for hs in hoc_sinh_ids:
        lk = random.choice(lopkhoa_ids)
        h = HocSinhLopHocKhoa(id_hs=hs[0], id_lop_khoa=lk[0])
        db.session.add(h)

    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        # Tạo models cho stu_manage_db
        db.create_all()
        # Nạp data các model vào db
        load_user_to_db('data/user.json')
        load_monhoc_to_db('data/monhoc.json')
        load_lophoc_to_db('data/lophoc.json')
        load_khoa_to_db('data/khoa.json')
        load_quy_dinh_to_db('data/quydinh.json')
        add_lop_to_khoa()
        add_hocsinh_to_lopkhoa()
        load_hs_to_db('data/hocsinh.json')
        add_hs_to_lopkhoa()

        # test()
