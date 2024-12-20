import cloudinary.uploader
from flask import Flask, render_template, request, redirect, url_for, jsonify
import dao
from app import app, login, db
from flask_login import login_user, logout_user, login_required
from app.models import UserRole, Grade, LopHoc
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
            if user:
                login_user(user=user)
                if user.get_role() == UserRole.ADMIN:
                    return redirect('/admin')
                if user.get_role() == UserRole.TEACHER:
                    return redirect('/scores-input')
                if user.get_role() == UserRole.STAFF:
                    return redirect('/addstudents')
                if user.get_role() == UserRole.STUDENT:
                    return redirect('/')

    return render_template('login.html')


# Logout
@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/login')


# add student
@app.route("/addstudents", methods=["get", "post"])
def add_student():
    if request.method.__eq__('POST'):
        ho_ten = request.form.get('ho_ten')
        gioi_tinh = int(request.form.get('gioi_tinh'))
        ngay_sinh = datetime.strptime(request.form.get('ngay_sinh'), '%Y-%m-%d')
        dia_chi = request.form.get('dia_chi')
        email = request.form.get('email')
        avatar = request.files.get('avatar')
        if avatar:
            res = cloudinary.uploader.upload(avatar)
            avatar = res.get('secure_url')
        hs = dao.add_stu(ho_ten=ho_ten,
                         gioi_tinh=gioi_tinh,
                         ngay_sinh=ngay_sinh,
                         dia_chi=dia_chi,
                         email=email,
                         avatar=avatar)

        dao.add_hs_to_lop(id_hs=hs, id_lop=dao.random_id_lop())
    return render_template('student_admissions.html')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


# Nhập điểm
@app.route("/scores-input")
def scores_input_view():
    return render_template('scores-input.html')


@app.route("/create-class-list")
def class_list_view():
    nien_khoa = dao.get_nien_khoa()
    khoi = dao.get_khoi()
    return render_template('class_list.html', khoi=khoi, nien_khoa=nien_khoa)


@app.route('/api/get_lop_by_khoi', methods=['POST'])
def get_lop_by_khoi():
    data = request.json
    khoi_input = data.get('khoi_value')
    khoi = str('Grade_' + khoi_input)
    print(khoi)
    ds_lop = dao.get_lophoc_by_khoi(khoi)
    print(ds_lop)
    formatted_lop = [{"ten_lop": lop} for lop in ds_lop]
    print(formatted_lop)
    return jsonify(formatted_lop), 200


if __name__ == "__main__":
    with app.app_context():
        from app import admin

        app.run(debug=True)
