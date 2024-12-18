
from flask import Flask, render_template, request, redirect, url_for
from pymysql import DATETIME

import dao
from app import app, login, db
from flask_login import login_user, logout_user, login_required
from app.models import HocSinh

from datetime import datetime


# Trang chủ
@app.route("/")
def index():
    return render_template("index.html")


# Login
@app.route("/login", methods=['get', 'post'])
def login_view():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
            return redirect('/')

    return render_template('login.html')


# Logout
@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/login')


#add student
@app.route("/addstudents", methods=["get", "post"])
def add_student():
    if request.method.__eq__('POST'):
        ho_ten = request.form.get('ho_ten')
        gioi_tinh = int(request.form.get('gioi_tinh'))
        ngay_sinh = datetime.strptime(request.form.get('ngay_sinh'), '%Y-%m-%d')
        dia_chi = request.form.get('dia_chi')
        email = request.form.get('email')

        hs = HocSinh(
            ho_ten=ho_ten,
            gioi_tinh=gioi_tinh,
            ngay_sinh=ngay_sinh,
            dia_chi=dia_chi,
            email=email
        )
        # Thêm dữ liệu vào

        db.session.add(hs)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('student_admissions.html')






# Login với admin
# @app.route("/login-admin", methods=['post'])
# def login_admin_view():
#     username = request.form.get('username')
#     password = request.form.get('password')
#     user = dao.auth_user(username=username, password=password, role=UserRole.ADMIN)
#     if user:
#         login_user(user=user)
#
#     return redirect("/admin")



@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


# Nhập điểm
@app.route("/scores-input")
def scores_input_view():
    return render_template('scores-input.html')



if __name__ == "__main__":
    with app.app_context():
        from app import admin
        app.run(debug=True)


# Login với admin
# @app.route("/login-admin", methods=['post'])
# def login_admin_view():
#     username = request.form.get('username')
#     password = request.form.get('password')
#     user = dao.auth_user(username=username, password=password, role=UserRole.ADMIN)
#     if user:
#         login_user(user=user)
#
#     return redirect("/admin")



@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


# Nhập điểm
@app.route("/scores-input")
def scores_input_view():
    return render_template('scores-input.html')



if __name__ == "__main__":
    with app.app_context():
        from app import admin
        app.run(debug=True)
