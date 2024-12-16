from datetime import datetime
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum
from app import db, app
from enum import Enum as RoleEnum
import hashlib
from flask_login import UserMixin


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
    name = Column(String(255), nullable=False)
    birthday = Column(DATETIME, nullable=False)
    address = Column(String(255), nullable=False)
    sex = Column(Integer, nullable=False)
    email = Column(String(100), nullable=False)
    user_role = Column(Enum(UserRole))

    def __str__(self):
        return self.name


class HocSinh(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    fullname = Column(String(100), nullable=False)
    sex = Column(Integer, nullable=False)
    birthday = Column(DATETIME, nullable=False)
    address = Column(String(255), nullable=False)
    email = Column(String(100), nullable=False)
    id_bang_diem = relationship('BangDiem', backref='hoc_sinh', lazy=False)


class BangDiem(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    mon_hoc = relationship('MonHoc', backref='bang_diem', lazy=False)
    hoc_ky = relationship('HocKy', backref='bang_diem', lazy=True)
    id_hoc_sinh = Column(Integer, ForeignKey(HocSinh.id), nullable=False)


class MonHoc(db.Model):
    ma_mon_hoc = Column(Integer, primary_key=True, autoincrement=True)
    ten_mon_hoc = Column(String(100), nullable=False)
    ma_bang_diem = Column(Integer, ForeignKey(BangDiem.id), nullable=False)


class Classroom(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    si_so = Column(Integer, nullable=False)
    grade = Column(Enum(Grade))


class HocKy(db.Model):
    ma_hk = Column(String(50), primary_key=True)
    nam_hoc = Column(String(50), nullable=False)
    id_bang_diem = Column(Integer, ForeignKey(BangDiem.id), nullable=False)


class ChiTietDiem(db.Model):
    id = Column(String(50), primary_key=True)
    type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    note = Column(String(100), nullable=True)


class Lop_MonHoc(db.Model):
    ma_lop = Column(Integer, ForeignKey(Classroom.id), primary_key=True)
    ma_mh = Column(Integer, ForeignKey(MonHoc.ma_mon_hoc), primary_key=True)


class HocSinh_Lop(db.Model):
    ma_hs = Column(Integer, ForeignKey(HocSinh.id), primary_key=True)
    ma_lop = Column(Integer, ForeignKey(Classroom.id), primary_key=True)


class User_MonHoc(db.Model):
    id_user = Column(Integer, ForeignKey(User.id), primary_key=True)
    ma_lop = Column(Integer, ForeignKey(Classroom.id), primary_key=True)
    ma_mh = Column(Integer, ForeignKey(MonHoc.ma_mon_hoc), primary_key=True)


class ChiTietDiem_BangDiem(db.Model):
    ma_bang_diem = Column(Integer, ForeignKey(BangDiem.id), primary_key=True)
    ma_diem = Column(String(50), ForeignKey(ChiTietDiem.id), primary_key=True)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        u = User(name="Trần Trung Hậu", username="tthau",
             password=str(hashlib.md5("12345".encode('utf-8')).hexdigest()),
             birthday=datetime.strptime("2004-10-08", "%Y-%m-%d"), address="TP.HCM", sex=1,
             email="2251050029hau@ou.edu.vn", user_role=UserRole.ADMIN)
        db.session.add(u)
        db.session.commit()
    # data_user = [{
    #     "name" : "Trần Trung Hậu",
    # "username" :"tthau"
    # "password" : str(hashlib.md5("12345".encode('utf-8')).hexdigest())
    # "birthday" :
    # "address" :
    # "sex" :
    # "email" :
    # "user_role" :
    # }, {
    #
    # }]