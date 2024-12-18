import math
from flask import render_template, request, redirect, session, jsonify
import dao
from app import app, login
from flask_login import login_user, logout_user, login_required
from app.models import UserRole


# Trang chủ
@app.route("/")
def index():
    return render_template("index.html")


""" Login user """
@app.route("/login", methods=['get', 'post'])
def login_view():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
            if user.get_role() == UserRole.ADMIN:
                return redirect('/admin')
            if user.get_role() == UserRole.TEACHER:
                return redirect('/nhap_diem')
            if user.get_role() == UserRole.STAFF:
                return redirect('/')

    return render_template('login.html')


# Logout
@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/login')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


# Nhập điểm
@app.route("/nhap_diem")
def scores_input_view():
    return render_template('nhap_diem.html')



if __name__ == "__main__":
    with app.app_context():
        from app import admin
        app.run(debug=True)
