from flask import Flask, render_template, request, redirect
import dao
from app import app, login
from flask_login import login_user, logout_user, login_required


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
