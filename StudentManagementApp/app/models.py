import json
import random
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime
from app import db, app
from enum import Enum as RoleEnum
import hashlib
from flask_login import UserMixin
from app import data


class UserRole(RoleEnum):
    ADMIN = 1
    TEACHER = 2
    STAFF = 3
    STUDENT = 4


class Grade(RoleEnum):
    Grade_10 = 1
    Grade_11 = 2
    Grade_12 = 3


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    ho_ten = Column(String(255), nullable=False)
    ngay_sinh = Column(DateTime, nullable=False)
    dia_chi = Column(String(255), nullable=False)
    """Nam: 0 -  Nữ: 1"""
    gioi_tinh = Column(Integer, nullable=False)
    email = Column(String(100), nullable=False)
    avatar = Column(String(255), nullable=True)
    user_role = Column(Enum(UserRole))

    def __str__(self):
        return self.ho_ten

    def get_role(self):
        return self.user_role


class HocSinh(User):
    id = Column(Integer, ForeignKey(User.id), primary_key=True, autoincrement=True)
    id_bang_diem = relationship('BangDiem', backref='hoc_sinh', lazy=False)

    def __str__(self):
        return self.ho_ten


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
        return self.ten_lop


class HocKy(db.Model):
    ma_hk = Column(String(50), primary_key=True)
    nam_hoc = Column(String(50), nullable=False)
    id_bang_diem = Column(Integer, ForeignKey(BangDiem.id), nullable=True)

    def __str__(self):
        hoc_ky = f"Học kì {self.ma_hk[-1]}" if self.ma_hk else ''
        return hoc_ky


class ChiTietDiem(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    gia_tri = Column(Float, default=0)


class LoaiDiem(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_loai = Column(String(50), nullable=False)


class TinNhan(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    noi_dung = Column(String(255), nullable=False)
    thoi_gian = Column(DateTime, default=datetime.now())
    id_gv = Column(Integer, ForeignKey(User.id), nullable=True)
    id_hs = Column(Integer, ForeignKey(HocSinh.id), nullable=True)


class LoaiDiemChiTietDiem(db.Model):
    lan = Column(Integer, primary_key=True)
    id_loai_diem = Column(Integer, ForeignKey(LoaiDiem.id), primary_key=True)
    id_chitiet_diem = Column(Integer, ForeignKey(ChiTietDiem.id))


class LopHocMonHoc(db.Model):
    ma_lop = Column(Integer, ForeignKey(LopHoc.id), primary_key=True)
    ma_mh = Column(Integer, ForeignKey(MonHoc.ma_mon_hoc), primary_key=True)


class HocSinhLopHoc(db.Model):
    ma_hs = Column(Integer, ForeignKey(HocSinh.id), primary_key=True)
    ma_lop = Column(Integer, ForeignKey(LopHoc.id), primary_key=True)


class UserMonHoc(db.Model):
    id_user = Column(Integer, ForeignKey(User.id), primary_key=True)
    ma_mh = Column(Integer, ForeignKey(MonHoc.ma_mon_hoc), primary_key=True)


class BangDiemChiTietDiem(db.Model):
    ma_bang_diem = Column(Integer, ForeignKey(BangDiem.id), primary_key=True)
    ma_diem = Column(Integer, ForeignKey(ChiTietDiem.id), primary_key=True)


class LopHocHocKy(db.Model):
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
                    avatar=item['avatar'],
                    user_role=item['user_role'])
        db.session.add(user)
    db.session.commit()


def load_stu_to_db(json_file):
    data = read_json_file(json_file)

    for item in data:
        student = HocSinh(ho_ten=item['ho_ten'],
                          username=item['username'],
                          password=str(hashlib.md5(item['password'].encode('utf-8')).hexdigest()),
                          gioi_tinh=item['gioi_tinh'],
                          ngay_sinh=item['ngay_sinh'],
                          dia_chi=item['dia_chi'],
                          email=item['email'],
                          user_role=UserRole.STUDENT
                          )
        db.session.add(student)
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


def load_hocky_to_db(json_file):
    data = read_json_file(json_file)

    for item in data:
        hk = HocKy(ma_hk=str(item['ma_hk']),
                   nam_hoc=item['nam_hoc'])
        db.session.add(hk)
    db.session.commit()


def load_loaidiem_to_db(json_file):
    data = read_json_file(json_file)

    for item in data:
        ld = LoaiDiem(ten_loai=item['ten_loai'])
        db.session.add(ld)
    db.session.commit()


def add_hocsinh_to_lop():
    hs = HocSinh.query.all()
    lop = LopHoc.query.all()
    for s in hs:
        lophoc = random.choice(lop)
        hs_lop = HocSinhLopHoc(ma_hs=s.id, ma_lop=lophoc.id)
        db.session.add(hs_lop)
    db.session.commit()


def add_lop_to_monhoc():
    lop = LopHoc.query.all()
    monhoc = MonHoc.query.all()

    for l in lop:
        for mh in monhoc:
            lop_mon = LopHocMonHoc(ma_lop=l.id, ma_mh=mh.ma_mon_hoc)
            db.session.add(lop_mon)

    db.session.commit()


def add_teacher_to_monhoc():
    teachers = User.query.filter_by(user_role=UserRole.TEACHER).all()
    monhoc = MonHoc.query.all()
    for t in teachers:
        mh = random.choice(monhoc)
        teach = UserMonHoc(id_user=t.id, ma_mh=mh.ma_mon_hoc)
        db.session.add(teach)
    db.session.commit()


def add_lop_to_hocky():
    lop = LopHoc.query.all()
    hocky = HocKy.query.all()
    for l in lop:
        for hk in hocky:
            lop_hk = LopHocHocKy(id_lop=l.id, id_hoc_ky=hk.ma_hk)
            db.session.add(lop_hk)
    db.session.commit()


def add_stu_to_score():
    students = HocSinh.query.all()
    for stu in students:
        bd = BangDiem.query.filter_by(id_hoc_sinh=stu.id).first()
        if not bd:
            bang_diem = BangDiem(id_hoc_sinh=stu.id)
            db.session.add(bang_diem)

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
        load_hocky_to_db('data/hocky.json')
        add_hocsinh_to_lop()
        add_lop_to_monhoc()
        add_teacher_to_monhoc()
        add_lop_to_hocky()
        load_loaidiem_to_db('data/loaidiem.json')