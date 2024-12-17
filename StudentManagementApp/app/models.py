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


class Classroom(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    si_so = Column(Integer, nullable=False)
    grade = Column(Enum(Grade))

    def __str__(self):
        return self.name


class HocKy(db.Model):
    ma_hk = Column(String(50), primary_key=True)
    nam_hoc = Column(String(50), nullable=False)
    id_bang_diem = Column(Integer, ForeignKey(BangDiem.id), nullable=False)

    def __str__(self):
        return self.ma_hk


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
        u1 = User(name="Trần Trung Hậu", username="tthau123",
                  password=str(hashlib.md5("12345".encode('utf-8')).hexdigest()),
                  birthday=datetime.strptime("2004-10-08", "%Y-%m-%d"), address="TP.HCM", sex=1,
                  email="tthau@ou.edu.vn", user_role=UserRole.ADMIN)

        u2 = User(name="Nguyễn Văn A", username="nva",
                  password=str(hashlib.md5("abc123".encode('utf-8')).hexdigest()),
                  birthday=datetime.strptime("2001-01-05", "%Y-%m-%d"), address="TP.HCM", sex=1,
                  email="nva@ou.edu.vn", user_role=UserRole.STAFF)

        u3 = User(name="Trần Thị B", username="ttb",
                  password=str(hashlib.md5("ttb123".encode('utf-8')).hexdigest()),
                  birthday=datetime.strptime("2004-10-08", "%Y-%m-%d"), address="Thủ Đức", sex=1,
                  email="2251050029hau@ou.edu.vn", user_role=UserRole.ADMIN)

        u4 = User(name="Trần Thanh Sang", username="ttsang",
                  password=str(hashlib.md5("2323".encode('utf-8')).hexdigest()),
                  birthday=datetime.strptime("2003-03-02", "%Y-%m-%d"), address="Nhà Bè", sex=1,
                  email="2253012087sang@ou.edu.vn", user_role=UserRole.STAFF)

        u5 = User(name="Phạm Văn Bé", username="pvb456",
                  password=str(hashlib.md5("pvb1234".encode('utf-8')).hexdigest()),
                  birthday=datetime.strptime("2003-10-04", "%Y-%m-%d"), address="Quận 7", sex=1,
                  email="pvb@ou.edu.vn", user_role=UserRole.TEACHER)

        db.session.add_all([u1, u2, u3, u4, u5])
        db.session.commit()

        data_hs = [{
            'fullname': 'Trần Văn Hậu',
            'sex': 1,
            'birthday': '2004-10-08',
            'address': 'Bến Tre',
            'email': 'tvh@gmail.com'
        }, {
            'fullname': 'Nguyễn Văn Ba',
            'sex': 1,
            'birthday': '2004-05-10',
            'address': 'Bình Thuận',
            'email': 'nvb@gmail.com'
        }, {
            'fullname': 'Phạm Thu Phương',
            'sex': 2,
            'birthday': '2004-12-12',
            'address': 'TP.Hồ Chí Minh',
            'email': 'ptp@gmail.com'
        }]

        for h in data_hs:
            hs = HocSinh(fullname=h['fullname'],
                         sex=h['sex'],
                         birthday=h['birthday'],
                         address=h['address'],
                         email=h['email'])
            db.session.add(hs)

        db.session.commit()

        data_mh = [{
            'ten_mon_hoc': 'Toán'
        }, {
            'ten_mon_hoc': 'Ngữ văn'
        }, {
            'ten_mon_hoc': 'Tiếng anh'
        }, {
            'ten_mon_hoc': 'Hoá học'
        }, {
            'ten_mon_hoc': 'Vật lý'
        }]

        for mh in data_mh:
            mh = HocSinh(ten_mon_hoc=mh['ten_mon_hoc'])

            db.session.add(mh)

        db.session.commit()
