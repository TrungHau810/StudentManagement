from flask import redirect
from flask_login import current_user, logout_user
from app import db, app, dao, models
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app.models import (User, HocSinh, UserRole,
                        GioiTinh, MonHoc, LopHoc,
                        Khoa, Diem, KetQuaHocTap,
                        LopHocKhoa, HocSinhLopHocKhoa,
                        GiaoVienMonHoc, GiaoVienMonHocLopHocKhoa,
                        HocKy, Khoi, LoaiDiem)
from flask_admin import BaseView, expose

admin = Admin(app, name='Student Manage System', template_mode='bootstrap4')


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)


class HocSinhView(AuthenticatedView):
    # Format 'ngay_sinh': dmy
    column_formatters = {
        'ngay_sinh': lambda v, c, m, p: m.ngay_sinh.strftime('%d/%m/%Y') if m.ngay_sinh else '',
        'gioi_tinh': lambda v, c, m, p: "Nam" if m.gioi_tinh == 0 else "Nữ"
    }
    column_labels = {
        'ho_ten': 'Họ tên',
        'gioi_tinh': 'Giới tính',
        'ngay_sinh': 'Ngày sinh',
        'dia_chi': 'Địa chỉ',
        'email': 'Email'
    }


class UserView(AuthenticatedView):
    column_formatters = {
        'ngay_sinh': lambda v, c, m, p: m.ngay_sinh.strftime('%d/%m/%Y') if m.ngay_sinh else '',
        'gioi_tinh': lambda v, c, m, p: "Nam" if m.gioi_tinh == 0 else "Nữ"
    }
    column_labels = {
        'ho_ten': 'Họ tên',
        'gioi_tinh': 'Giới tính',
        'ngay_sinh': 'Ngày sinh',
        'dia_chi': 'Địa chỉ',
        'email': 'Email'
    }
    column_filters = ['user_role']


class MonHocView(AuthenticatedView):
    column_labels = {
        'ten_mon_hoc': 'Tên môn học'
    }
    column_exclude_list = ('ma_bang_diem',)


class KetQuaHocTapView(AuthenticatedView):
    pass
    # models.add_stu_to_score()


class ChiTietDiemView(AuthenticatedView):
    pass


class HocSinhLopHocView(AuthenticatedView):
    pass


class MyView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(MyView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/')


admin.add_view(UserView(User, db.session))
admin.add_view(MonHocView(MonHoc, db.session, name="Môn học"))
admin.add_view(ModelView(LopHoc, db.session, name="Lớp học"))
admin.add_view(ModelView(Khoa, db.session, name="Năm học"))
admin.add_view(ModelView(LopHocKhoa, db.session, name="Lớp-Năm học"))
# admin.add_view(HocSinhView(User, db.session, name="Học sinh"))
admin.add_view(KetQuaHocTapView(KetQuaHocTap, db.session, name="Bảng điểm"))
admin.add_view(HocSinhLopHocView(HocSinhLopHocKhoa, db.session, name="Danh sách học sinh với lớp"))
admin.add_view(LogoutView(name='Đăng xuất'))
