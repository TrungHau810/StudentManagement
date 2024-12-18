import json
from datetime import datetime
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum
from app import db, app
from enum import Enum as RoleEnum
import hashlib
from flask_login import UserMixin
from app import data


class UserRole(RoleEnum):
    ADMIN = 1,
    TEACHER = 2,
    STAFF = 3


class Grade(RoleEnum):
    Grade_10 = 1
    Grade_11 = 2
    Grade_12 = 3


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    ho_ten = Column(String(255), nullable=False)
    ngay_sinh = Column(DATETIME, nullable=False)
    dia_chi = Column(String(255), nullable=False)
    gioi_tinh = Column(Integer, nullable=False)
    email = Column(String(100), nullable=False)
    user_role = Column(Enum(UserRole))

    def __str__(self):
        return self.name

    def get_role(self):
        return self.user_role


class HocSinh(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ho_ten = Column(String(100), nullable=False)
    gioi_tinh = Column(Integer, nullable=False)
    ngay_sinh = Column(DATETIME, nullable=False)
    dia_chi = Column(String(255), nullable=False)
    email = Column(String(100), nullable=False)
    id_bang_diem = relationship('BangDiem', backref='hoc_sinh', lazy=False)

    def __str__(self):
        return self.fullname


class BangDiem(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    mon_hoc = relationship('MonHoc', backref='bang_diem', lazy=False)
    hoc_ky = relationship('HocKy', backref='bang_diem', lazy=True)
    id_hoc_sinh = Column(Integer, ForeignKey(HocSinh.id), nullable=False)

    def __str__(self):
        return self.id


class MonHoc(db.Model):
    ma_mon_hoc = Column(Integer, primary_key=True, autoincrement=True)
    ten_mon_hoc = Column(String(100), nullable=False)
    ma_bang_diem = Column(Integer, ForeignKey(BangDiem.id))

    def __str__(self):
        return self.ten_mon_hoc


class LopHoc(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_lop = Column(String(100), nullable=False)
    si_so = Column(Integer, nullable=False)
    khoi = Column(Enum(Grade))

    def __str__(self):
        return self.name


class HocKy(db.Model):
    ma_hk = Column(String(50), primary_key=True)
    nam_hoc = Column(String(50), nullable=False)
    id_bang_diem = Column(Integer, ForeignKey(BangDiem.id), nullable=False)

    def __str__(self):
        hoc_ky = f"Học kì {self.ma_hk[-1]}" if self.ma_hk else ''
        return hoc_ky


class ChiTietDiem(db.Model):
    id = Column(String(50), primary_key=True)
    loai_diem = Column(String(50), nullable=False)
    gia_tri = Column(Float, nullable=False)
    ghi_chu = Column(String(100), nullable=True)


class Lop_MonHoc(db.Model):
    ma_lop = Column(Integer, ForeignKey(LopHoc.id), primary_key=True)
    ma_mh = Column(Integer, ForeignKey(MonHoc.ma_mon_hoc), primary_key=True)


class HocSinh_Lop(db.Model):
    ma_hs = Column(Integer, ForeignKey(HocSinh.id), primary_key=True)
    ma_lop = Column(Integer, ForeignKey(LopHoc.id), primary_key=True)


class User_MonHoc(db.Model):
    id_user = Column(Integer, ForeignKey(User.id), primary_key=True)
    ma_lop = Column(Integer, ForeignKey(LopHoc.id), primary_key=True)
    ma_mh = Column(Integer, ForeignKey(MonHoc.ma_mon_hoc), primary_key=True)


class ChiTietDiem_BangDiem(db.Model):
    ma_bang_diem = Column(Integer, ForeignKey(BangDiem.id), primary_key=True)
    ma_diem = Column(String(50), ForeignKey(ChiTietDiem.id), primary_key=True)


class Lop_HocKy(db.Model):
    id_lop = Column(Integer, ForeignKey(LopHoc.id), primary_key=True)
    id_hoc_ky = Column(String(50), ForeignKey(HocKy.ma_hk), primary_key=True)


# Open file json
def read_json_file(json_file):
    with open(json_file, encoding='utf-8') as file:
        return json.load(file)


def load_user_to_db(json_file):
    data = read_json_file(json_file)

    for item in data:
        user = User(ho_ten=item['ho_ten'],
                    username=item['username'],
                    password=str(hashlib.md5(item['password'].encode('utf-8')).hexdigest()),
                    ngay_sinh=datetime.strptime(item['ngay_sinh'], "%Y-%m-%d"),
                    dia_chi=item['dia_chi'],
                    gioi_tinh=item['gioi_tinh'],
                    email=item['email'],
                    user_role=item['user_role'])
        db.session.add(user)
    db.session.commit()


def load_monhoc_to_db(json_file):
    data = read_json_file(json_file)

    for item in data:
        mh = MonHoc(ten_mon_hoc=item['ten_mon_hoc'])
        db.session.add(mh)
    db.session.commit()


def load_stu_to_db(json_file):
    data = read_json_file(json_file)

    for item in data:
        student = HocSinh(ho_ten=item['ho_ten'],
                          gioi_tinh=item['gioi_tinh'],
                          ngay_sinh=item['ngay_sinh'],
                          dia_chi=item['dia_chi'],
                          email=item['email'])
        db.session.add(student)
    db.session.commit()


def load_lophoc_to_db(json_file):
    data = read_json_file(json_file)

    for item in data:
        lop = LopHoc(ten_lop=item['ten_lop'],
                     si_so=item['si_so'],
                     khoi=item['khoi'])
        db.session.add(lop)
    db.session.commit()


def load_hocky_to_db(json_file):
    data = read_json_file(json_file)

    for item in data:
        hk = HocKy(ma_hk=item['ma_hk'],
                   nam_hoc=item['nam_hoc'])
        db.session.add(hk)
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        # Tạo models cho stu_manage_db
        db.create_all()
        # Nạp data các model vào db
        load_user_to_db('data/user.json')
        load_stu_to_db('data/hocsinh.json')
        load_monhoc_to_db('data/monhoc.json')
        load_lophoc_to_db('data/lophoc.json')
