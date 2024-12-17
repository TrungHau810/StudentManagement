from tkinter.font import names

from app import db, app, dao
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app.models import User, MonHoc, HocSinh, BangDiem, ChiTietDiem, ChiTietDiem_BangDiem, HocKy, HocSinh_Lop

admin = Admin(app, name='Student Manage System', template_mode='bootstrap4')


class HocSinhView(ModelView):
    # Format 'ngay_sinh': dmy
    column_formatters = {
        'birthday': lambda v, c, m, p: m.birthday.strftime('%d/%m/%Y') if m.birthday else '',
        'sex': lambda v, c, m, p: "Nam" if m.sex == 1 else  "Nữ"
    }
    column_labels = {
        'fullname': 'Họ tên',  # Đổi tên cột 'fullname' thành 'Họ và Tên'
        'sex': 'Giới tính',  # Đổi tên cột 'sex' thành 'Giới Tính'
        'birthday': 'Ngày sinh',  # Đổi tên cột 'birthday' thành 'Ngày Sinh'
        'address': 'Địa chỉ',  # Đổi tên cột 'address' thành 'Địa Chỉ'
        'email': 'Email'  # Đổi tên cột 'email' thành 'Email'
    }


class MonHocView(ModelView):
    column_labels = {
        'ten_mon_hoc': 'Tên môn học'
    }

class BangDiemView(ModelView):
    dao.add_stu_to_score()




admin.add_view(ModelView(User, db.session))
admin.add_view(MonHocView(MonHoc, db.session, name="Môn học"))
admin.add_view(HocSinhView(HocSinh, db.session, name="Học sinh"))
admin.add_view(BangDiemView(BangDiem, db.session, name="Bảng điểm"))
admin.add_view(ModelView(ChiTietDiem, db.session, name="Bảng điểm chi tiết"))
