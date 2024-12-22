import cloudinary.uploader
from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy.dialects.postgresql import hstore

import dao
from app import app, login, db
from flask_login import login_user, logout_user, login_required

from app.dao import get_id_khoa_by_ten_khoa, get_id_lop_by_ten_lop, get_id_lopkhoa_by_id_lop_khoa, \
    get_list_id_hs_by_id_lopkhoa, get_hs_info_by_id_hs, get_all_lop
from app.models import UserRole, Khoi, LopHoc
from datetime import datetime
from app.models import (User, HocSinh, UserRole,
                        GioiTinh, MonHoc, LopHoc,
                        Khoa, Diem, KetQuaHocTap,
                        LopHocKhoa, HocSinhLopHocKhoa,
                        GiaoVienMonHoc, GiaoVienMonHocLopHocKhoa,
                        HocKy, Khoi, LoaiDiem)


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
        gioi_tinh_str = request.form.get('gioi_tinh')
        gioi_tinh = GioiTinh[gioi_tinh_str]
        ngay_sinh = datetime.strptime(request.form.get('ngay_sinh'), '%Y-%m-%d')
        dia_chi = request.form.get('dia_chi')
        email = request.form.get('email')
        so_dien_thoai = request.form.get('so-dien-thoai')

        current_date = datetime.now()

        # tính tuổi
        age_now = current_date.year - ngay_sinh.year - (
                (current_date.month, current_date.day) < (ngay_sinh.month, ngay_sinh.day))

        if age_now >= 15:
            dao.add_stu(ho_ten=ho_ten,
                        gioi_tinh=gioi_tinh,
                        ngay_sinh=ngay_sinh,
                        dia_chi=dia_chi,
                        so_dien_thoai=so_dien_thoai,
                        email=email)

            # dao.add_hs_to_lop(id_hs=hs, id_lop=dao.random_id_lop())
            message = "Thêm học sinh thành công"
        else:
            message = "Thêm học sinh thất bại, học sinh phải đủ 15 tuổi"

        return render_template('student_admissions.html', message=message)

    return render_template('student_admissions.html')


@app.route('/scores-input', methods=['GET'])
@login_required
def nhap_diem():
    # Lấy danh sách năm học
    nam_hoc = dao.get_nam_hoc()
    return render_template('scores-input.html', nam_hoc=nam_hoc)


@app.route('/api/get_namhoc', methods=['GET'])
def get_namhoc():
    try:
        nam_hoc = db.session.query(Khoa.ten_khoa).distinct().all()
        nam_hoc_list = [nh.ten_khoa for nh in nam_hoc]
        return jsonify(nam_hoc_list)
    except Exception as ex:
        return jsonify({'error': str(ex)}), 400
@app.route('/api/get_hocky_by_namhoc', methods=['POST'])
def get_hocky():
    try:
        data = request.get_json()
        nam_hoc = data.get('nam_hoc')
        # Lấy học kỳ theo năm học
        hoc_ky = db.session.query(Khoa.hoc_ky).filter(Khoa.ten_khoa == nam_hoc).all()
        return jsonify({
            'hoc_ky': [{'id': hk.hoc_ky.name, 'ten': hk.hoc_ky.value} for hk in hoc_ky]
        })
    except Exception as ex:
        return jsonify({'error': str(ex)}), 400

@app.route('/api/get_lop_by_namhoc_hocky', methods=['POST'])
def get_lop():
    try:
        data = request.get_json()
        nam_hoc = data.get('nam_hoc')
        hoc_ky = data.get('hoc_ky')

        # Lấy danh sách lớp theo năm học và học kỳ
        lop_list = (db.session.query(LopHoc)
                    .join(LopHocKhoa)
                    .join(Khoa)
                    .filter(Khoa.ten_khoa == nam_hoc,
                            Khoa.hoc_ky == hoc_ky)
                    .all())

        return jsonify({
            'lop': [{'id': lop.id, 'ten': lop.ten_lop} for lop in lop_list]
        })
    except Exception as ex:
        return jsonify({'error': str(ex)}), 400

@app.route('/api/get_students_and_subjects', methods=['POST'])
def get_students_subjects():
    try:
        data = request.get_json()
        nam_hoc = data.get('nam_hoc')
        hoc_ky = data.get('hoc_ky')
        lop_id = data.get('lop_id')

        # Lấy danh sách học sinh
        students = (db.session.query(HocSinh)
                    .join(HocSinhLopHocKhoa)
                    .join(LopHocKhoa)
                    .filter(LopHocKhoa.id_lop == lop_id)
                    .all())

        # Lấy danh sách môn học
        subjects = (db.session.query(MonHoc)
                    .join(GiaoVienMonHocLopHocKhoa)
                    .join(LopHocKhoa)
                    .filter(LopHocKhoa.id_lop == lop_id)
                    .all())

        return jsonify({
            'students': [{
                'id': hs.id,
                'ma_hs': f'HS{hs.id:03d}',
                'ho_ten': hs.ho_ten
            } for hs in students],
            'subjects': [{
                'id': mh.id,
                'ten': mh.ten_mon_hoc
            } for mh in subjects]
        })
    except Exception as ex:
        return jsonify({'error': str(ex)}), 400
@app.route('/api/save_scores', methods=['POST'])
def save_scores():
    try:
        data = request.get_json()
        scores = data.get('scores')
        hoc_ky = data.get('hoc_ky')

        for score in scores:
            diem = Diem(
                student_id=score['student_id'],
                subject_id=score['subject_id'],
                diem=score['diem'],
                hoc_ky=hoc_ky
            )
            db.session.add(diem)
        db.session.commit()

        return jsonify({'message': 'Lưu điểm thành công'})
    except Exception as ex:
        return jsonify({'error': str(ex)}), 400


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


# Nhập điểm

def scores_input_view():

    return render_template('scores-input.html')
@app.route('/api/get_hocsinh', methods=['POST'])
def get_hocsinh_1():
    data = request.get_json()
    nam_hoc = data.get('nam_hoc')
    ten_lop = data.get('ten_lop')

    id_khoa = get_id_khoa_by_ten_khoa(nam_hoc)
    id_lop = get_id_lop_by_ten_lop(ten_lop)
    id_lop_khoa = get_id_lopkhoa_by_id_lop_khoa(id_khoa, id_lop)
    list_id_hs = get_list_id_hs_by_id_lopkhoa(id_lop_khoa)

    return jsonify(get_hs_info_by_id_hs(list_id_hs))

@app.route("/create-class-list")
def class_list_view():
    khoi = dao.get_khoi()
    nam_hoc = dao.get_nam_hoc()
    return render_template('class_list.html', nam_hoc=nam_hoc, khoi=khoi)


@app.route('/api/get_lop_by_khoi', methods=['post'])
def get_lop_by_khoi_khoa():
    data = request.get_json()
    ten_khoi = data.get('ten_khoi')
    nam_hoc = data.get('nam_hoc')

    ds_lop = db.session.query(LopHoc.id, LopHoc.ten_lop) \
        .join(LopHocKhoa, LopHoc.id == LopHocKhoa.id_lop) \
        .join(Khoa, LopHocKhoa.id_khoa == Khoa.id) \
        .filter(LopHoc.khoi == ten_khoi, Khoa.ten_khoa == nam_hoc) \
        .distinct()

    lop_list = [{"id": lop.id, "ten_lop": lop.ten_lop} for lop in ds_lop]

    return jsonify(lop_list)


@app.route('/api/get_hocsinh', methods=['POST'])
def get_hocsinh():
    data = request.get_json()
    ten_khoi = data.get('ten_khoi')
    nam_hoc = data.get('nam_hoc')
    ten_lop = data.get('ten_lop')

    id_khoa = get_id_khoa_by_ten_khoa(nam_hoc)
    id_lop = get_id_lop_by_ten_lop(ten_lop)
    id_lop_khoa = get_id_lopkhoa_by_id_lop_khoa(id_khoa, id_lop)
    list_id_hs = get_list_id_hs_by_id_lopkhoa(id_lop_khoa)
    return jsonify({
        'hs': get_hs_info_by_id_hs(list_id_hs),
        'lop': get_all_lop()
    })


# @app.route("/api/change-lop-hs", metheds=['POST'])
# def change_lop_hocsinh():
#     data = request.get_json()
#     id_lop = data.get('id_lop')
#     nam_hoc = data.get('nam_hoc')
#
#     id_khoa = get_id_khoa_by_ten_khoa(nam_hoc)
#     id_khoalop = get_id_lopkhoa_by_id_lop_khoa(id_khoa, id_lop)
#     pass



@app.route('/api/add_hocsinh_to_lop', methods=['POST'])
def add_hocsinh():
    data = request.get_json()
    ten_khoi = data.get('ten_khoi')
    nam_hoc = data.get('nam_hoc')
    ten_lop = data.get('ten_lop')
    id_hocsinh = data.get('list')
    print(id_hocsinh)
    lop_list = LopHoc.query.filter_by(ten_lop=ten_lop).all()
    if lop_list:
        lop_id = lop_list[0].id

    khoa = Khoa.query.filter_by(ten_khoa=nam_hoc).first()
    if khoa:
        khoa_id = khoa.id

    id_lop_khoa = LopHocKhoa.query.filter_by(id_lop=lop_id, id_khoa=khoa_id).first()
    id_lop_khoa = id_lop_khoa.id

    for id in id_hocsinh:
        hs = HocSinhLopHocKhoa(id_hs=id, id_lop_khoa=id_lop_khoa)
        db.session.add(hs)
    db.session.commit()
    return jsonify({"message": "Thêm học sinh vào lớp thành công"})


if __name__ == "__main__":
    with app.app_context():
        from app import admin
        app.run(debug=True)
