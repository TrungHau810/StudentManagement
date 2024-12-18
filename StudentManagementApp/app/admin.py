from flask import redirect
from flask_login import current_user, logout_user
from app import db, app, dao
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app.models import User, MonHoc, HocSinh, BangDiem, ChiTietDiem, ChiTietDiem_BangDiem, HocKy, HocSinh_Lop
from flask_admin import BaseView, expose


admin = Admin(app, name='Student Manage System', template_mode='bootstrap4')


class HocSinhView(ModelView):
    # Format 'ngay_sinh': dmy
    column_formatters = {
        'ngay_sinh': lambda v, c, m, p: m.ngay_sinh.strftime('%d/%m/%Y') if m.ngay_sinh else '',
        'gioi_tinh': lambda v, c, m, p: "Nam" if m.gioi_tinh == 1 else "Nữ"
    }
    column_labels = {
        'fullname': 'Họ tên',
        'gioi_tinh': 'Giới tính',
        'ngay_sinh': 'Ngày sinh',
        'dia_chi': 'Địa chỉ',
        'email': 'Email'
    }


class MonHocView(ModelView):
    column_labels = {
        'ten_mon_hoc': 'Tên môn học'
    }

class BangDiemView(ModelView):
    dao.add_stu_to_score()


class MyView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(MyView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/')



admin.add_view(ModelView(User, db.session))
admin.add_view(MonHocView(MonHoc, db.session, name="Môn học"))
admin.add_view(HocSinhView(HocSinh, db.session, name="Học sinh"))
admin.add_view(BangDiemView(BangDiem, db.session, name="Bảng điểm"))
admin.add_view(ModelView(ChiTietDiem, db.session, name="Bảng điểm chi tiết"))
admin.add_view(LogoutView(name='Đăng xuất'))
