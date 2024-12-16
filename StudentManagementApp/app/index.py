from flask import Flask, render_template, request, redirect
import dao
from app import app
from app.models import UserRole
from  flask_login import login_user


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        u = dao.auth_user(username=username, password=password)
        if u:
            login_user(u)

            return redirect('/')

    return render_template('login.html')



if __name__ == "__main__":
    app.run(debug=True)
