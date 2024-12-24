import cloudinary.uploader
from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy.dialects.postgresql import hstore
from sqlalchemy import or_, and_
import dao
from app import app, login, db
from flask_login import login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired

from app.dao import get_id_khoa_by_ten_khoa, get_id_lop_by_ten_lop, get_id_lopkhoa_by_id_lop_khoa, \
    get_list_id_hs_by_id_lopkhoa, get_hs_info_by_id_hs, get_all_lop, get_all_subjects
from app.models import UserRole, Khoi, LopHoc
from datetime import datetime
from app.models import (User, HocSinh, UserRole,
                        GioiTinh, MonHoc, LopHoc,
                        Khoa, Diem, KetQuaHocTap,
                        LopHocKhoa, HocSinhLopHocKhoa,
                        GiaoVienMonHoc, GiaoVienMonHocLopHocKhoa,
                        HocKy, Khoi, LoaiDiem)


@app.route("/")
def index():
    return render_template("index.html")


class ClassListForm(FlaskForm):
    nam_hoc = SelectField('Năm học', validators=[DataRequired()])
    khoi = SelectField('Khối', validators=[DataRequired()])
    lop = SelectField('Lớp', validators=[DataRequired()])
    submit = SubmitField('Xác nhận')


# Form thêm học sinh vào lớp
class AddStudentToClassForm(FlaskForm):
    submit = SubmitField('Thêm vào lớp')


@app.route("//create-class-list", methods=['GET', 'POST'])
def class_list_view():
    form = ClassListForm()
    form_add = AddStudentToClassForm()
    khoi = Khoi
    nam_hoc = dao.get_nam_hoc()
    danh_sach_lop = dao.get_all_lop()

    form.nam_hoc.choices = [('', '-- Chọn năm --')] + [(nh, nh) for nh in nam_hoc]
    form.khoi.choices = [('', '-- Chọn khối --')] + [(k.name, k.value) for k in khoi]
    form.lop.choices = [('', '-- Chọn lớp --')] + [(lop['id'], lop['ten_lop']) for lop in danh_sach_lop]

    if form.validate_on_submit():
        # Xử lý logic khi submit form
        selected_nam_hoc = form.nam_hoc.data
        selected_khoi = form.khoi.data
        selected_lop_id = form.lop.data

        return redirect(
            url_for('class_list_view', nam_hoc=selected_nam_hoc, khoi=selected_khoi, lop_id=selected_lop_id))

    if form_add.validate_on_submit():
        pass

    return render_template('class_list.html', form=form, form_add=form_add, nam_hoc=nam_hoc, khoi=khoi,
                           danh_sach_lop=danh_sach_lop)


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

        if age_now >= 15 and age_now <= 20:

            dao.add_stu(ho_ten=ho_ten,
                        gioi_tinh=gioi_tinh,
                        ngay_sinh=ngay_sinh,
                        dia_chi=dia_chi,
                        so_dien_thoai=so_dien_thoai,
                        email=email)

            # dao.add_hs_to_lop(id_hs=hs, id_lop=dao.random_id_lop())
            message = "Thêm học sinh thành công"
        else:
            message = "Thêm học sinh thất bại, học sinh phải đủ 15 đến 20 tuổi"

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


@app.route('/api/get_all_subjects', methods=['POST'])
def get_mon():
    try:
        data = request.get_json()
        nam_hoc = data.get('nam_hoc')
        hoc_ky = data.get('hoc_ky')
        lop_id = data.get('lop')
        # Lấy id khóa từ năm học và học kỳ
        khoa_id = dao.get_khoa_id(nam_hoc, hoc_ky)

        # Lấy id_lop_khoa
        id_lop_khoa = dao.get_id_lop_khoa(khoa_id, lop_id)
        monhoc_list = (db.session.query(MonHoc)
                       .join(GiaoVienMonHocLopHocKhoa, MonHoc.id == GiaoVienMonHocLopHocKhoa.id_mon_hoc)
                       .filter(GiaoVienMonHocLopHocKhoa.id_lop_khoa == id_lop_khoa)
                       .distinct()
                       .all())

        if not monhoc_list:
            monhoc_list = MonHoc.query.all()

        result = [{
            'id': mon.id,
            'ten_mon_hoc': mon.ten_mon_hoc
        } for mon in monhoc_list]
        return jsonify(result)
    except Exception as ex:
        print(f"Error in get_mon: {str(ex)}")
    return jsonify({'error': str(ex)}), 400


@app.route('/api/get_monhoc_by_lop', methods=['POST'])
def get_monhoc_by_lop():
    try:
        data = request.get_json()
        lop_id = data.get('lop_id')
        hoc_ky = data.get('hoc_ky')
        nam_hoc = data.get('nam_hoc')

        khoa_id = dao.get_khoa_id(nam_hoc, hoc_ky)
        if not khoa_id:
            return jsonify({'error': 'Không tìm thấy khóa học'}), 404

        id_lop_khoa = dao.get_id_lop_khoa(khoa_id, lop_id)
        if not id_lop_khoa:
            return jsonify({'error': 'Không tìm thấy lớp trong khóa học này'}), 404

        mon_hoc = dao.get_monhoc_by_lopkhoa(id_lop_khoa)

        return jsonify({'mon_hoc': mon_hoc})
    except Exception as ex:
        print(f"Error in get_monhoc_by_lop: {str(ex)}")
        return jsonify({'error': str(ex)}), 400


@app.route('/api/test_data', methods=['GET'])
def test_data():
    try:
        # Kiểm tra số lượng môn học
        mon_hoc_count = MonHoc.query.count()

        # Kiểm tra số lượng phân công giáo viên
        gv_mon_hoc_count = GiaoVienMonHocLopHocKhoa.query.count()

        # Lấy danh sách tất cả môn học
        mon_hoc_list = MonHoc.query.all()
        mon_hoc_data = [{"id": mon.id, "ten": mon.ten_mon_hoc} for mon in mon_hoc_list]

        return jsonify({
            "so_mon_hoc": mon_hoc_count,
            "so_phan_cong": gv_mon_hoc_count,
            "danh_sach_mon": mon_hoc_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# @app.route('/api/get_students_and_subjects', methods=['POST'])
# def get_students_and_subjects():
#     try:
#         data = request.get_json()
#         lop_id = data.get('lop_id')
#         nam_hoc = data.get("namHoc")
#         hoc_ky = data.get('hocKy')
#
#         id_khoa = dao.get_khoa_id(nam_hoc, hoc_ky)  # Correctly using dao.get_khoa_id
#         id_lop_khoa_list = get_id_lopkhoa_by_id_lop_khoa([id_khoa], lop_id)  # Use the corrected function
#         hs_id = get_list_id_hs_by_id_lopkhoa(id_lop_khoa_list[0]) # Get the first id_lop_khoa
#         hs_info = get_hs_info_by_id_hs(hs_id)  # Get student info
#
#         return jsonify(hs_info)  # Return the student info
#
#     except Exception as ex:
#         return jsonify({'error': str(ex)}), 400


@app.route('/api/get_students_and_subjects', methods=['POST'])
def api_get_students_and_subjects():
    try:
        data = request.json
        lop_id = data.get('lop_id')
        hoc_ky = data.get('hocKy')
        nam_hoc = data.get('namHoc')
        mon_hoc_id = data.get('monHocId')

        # Lấy id_lopkhoa
        khoa_id = dao.get_khoa_id(nam_hoc, hoc_ky)
        if not khoa_id:
            return jsonify({'error': 'Không tìm thấy khóa học'}), 404

        id_lopkhoa = dao.get_id_lop_khoa(khoa_id, lop_id)
        if not id_lopkhoa:
            return jsonify({'error': 'Không tìm thấy lớp trong khóa học này'}), 404

        # Lấy danh sách học sinh và điểm
        students = dao.get_students_with_scores(id_lopkhoa, mon_hoc_id, hoc_ky)

        return jsonify({
            "students": students
        })
    except Exception as e:
        print(f"Error in api_get_students_and_subjects: {str(e)}")
        return jsonify({"error": str(e)}), 500


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


# @app.route("/create-class-list")
# def class_list_view():
#     khoi = dao.get_khoi()
#     nam_hoc = dao.get_nam_hoc()
#     return render_template('class_list.html', nam_hoc=nam_hoc, khoi=khoi)


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


@app.route('/api/get_hocsinh_not_in_class', methods=['POST'])
def get_hocsinh_not_in_class():
    try:
        data = request.get_json()
        nam_hoc = data.get('nam_hoc')
        khoi = data.get('khoi')
        lop_id = int(data.get('lop_id'))

        print(f"nam_hoc: {nam_hoc}, khoi: {khoi}, lop_id: {lop_id}")

        khoa_id_query = db.session.query(Khoa.id).filter(Khoa.ten_khoa == nam_hoc).first()

        if khoa_id_query is None:
            print("Không tìm thấy khoa với ten_khoa:", nam_hoc)
            return jsonify([])  # Trả về danh sách rỗng nếu không tìm thấy khoa

        khoa_id = khoa_id_query[0]  # Lấy ID từ kết quả truy vấn

        # 2. Lấy danh sách học sinh
        hocsinh_list = (db.session.query(HocSinh)
                        .outerjoin(HocSinhLopHocKhoa, HocSinh.id == HocSinhLopHocKhoa.id_hs)
                        .outerjoin(LopHocKhoa, HocSinhLopHocKhoa.id_lop_khoa == LopHocKhoa.id)
                        .outerjoin(LopHoc, LopHocKhoa.id_lop == LopHoc.id)
                        .outerjoin(Khoa, LopHocKhoa.id_khoa == Khoa.id)
                        .filter(
            or_(
                HocSinhLopHocKhoa.id_lop_khoa == None,
                and_(
                    Khoa.id == khoa_id,
                    LopHoc.khoi == khoi,
                    LopHoc.id != lop_id
                )
            ),
            HocSinh.ngay_sinh >= datetime.strptime(f"{int(nam_hoc.split('-')[0]) - 18}-01-01", "%Y-%m-%d"),
            HocSinh.ngay_sinh <= datetime.strptime(f"{int(nam_hoc.split('-')[0]) - 15}-12-31", "%Y-%m-%d")
        )
                        .all())

        print(f"hocsinh_list: {hocsinh_list}")

        hoc_sinh_info = [
            {
                "id": hs.id,
                "ho_ten": hs.ho_ten,
                "gioi_tinh": hs.gioi_tinh.value,
                "nam_sinh": hs.ngay_sinh.year,
                "dia_chi": hs.dia_chi,
                "selected": False
            }
            for hs in hocsinh_list
        ]

        return jsonify(hoc_sinh_info)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify([]), 500


@app.route('/api/save_scores', methods=['POST'])
def save_scores():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debug log

        scores = data.get('scores', [])
        mon_hoc_id = int(data.get('mon_hoc_id'))
        hoc_ky = data.get('hoc_ky')

        if not scores or not mon_hoc_id or not hoc_ky:
            return jsonify({'error': 'Thiếu thông tin điểm hoặc môn học'}), 400

        # Chuyển đổi học kỳ
        hoc_ky_enum = HocKy.HK1 if hoc_ky == "HK1" else HocKy.HK2

        # Lưu điểm
        for score in scores:
            student_id = int(score.get('student_id'))
            diem_tx = score.get('diem_tx')
            diem_gk = score.get('diem_gk')
            diem_ck = score.get('diem_ck')

            if diem_tx is not None:
                dao.save_diem(student_id, mon_hoc_id, float(diem_tx), LoaiDiem.DIEMTX, hoc_ky_enum)
            if diem_gk is not None:
                dao.save_diem(student_id, mon_hoc_id, float(diem_gk), LoaiDiem.DIEMGK, hoc_ky_enum)
            if diem_ck is not None:
                dao.save_diem(student_id, mon_hoc_id, float(diem_ck), LoaiDiem.DIEMCK, hoc_ky_enum)

        return jsonify({'message': 'Lưu điểm thành công'}), 200

    except Exception as e:
        print("Error saving scores:", str(e))  # Debug log
        return jsonify({'error': str(e)}), 500


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


# @app.route('/api/add_hocsinh_to_lop', methods=['POST'])
# def add_hocsinh():
#     data = request.get_json()
#     ten_khoi = data.get('ten_khoi')
#     nam_hoc = data.get('nam_hoc')
#     ten_lop = data.get('ten_lop')
#     id_hocsinh = data.get('list')
#     print(id_hocsinh)
#     lop_list = LopHoc.query.filter_by(ten_lop=ten_lop).all()
#     if lop_list:
#         lop_id = lop_list[0].id
#
#     khoa = Khoa.query.filter_by(ten_khoa=nam_hoc).first()
#     if khoa:
#         khoa_id = khoa.id
#
#     id_lop_khoa = LopHocKhoa.query.filter_by(id_lop=lop_id, id_khoa=khoa_id).first()
#     id_lop_khoa = id_lop_khoa.id
#
#     for id in id_hocsinh:
#         hs = HocSinhLopHocKhoa(id_hs=id, id_lop_khoa=id_lop_khoa)
#         db.session.add(hs)
#     db.session.commit()
#     return jsonify({"message": "Thêm học sinh vào lớp thành công"})

@app.route('/api/add_hocsinh_to_lop', methods=['POST'])
def add_hocsinh_to_lop():
    try:
        data = request.get_json()
        selected_students = data.get('selected_students')
        lop_id = data.get('lop_id')
        nam_hoc = data.get('nam_hoc')
        print(selected_students)
        print(lop_id)
        print(nam_hoc)

        if not selected_students or not lop_id or not nam_hoc:
            return jsonify({'message': 'Thiếu thông tin cần thiết'}), 400

        khoa = Khoa.query.filter_by(ten_khoa=nam_hoc).first()
        if not khoa:
            return jsonify({'message': 'Năm học không tồn tại'}), 400
        khoa_id = khoa.id

        lop_hoc_khoa = LopHocKhoa.query.filter_by(id_lop=lop_id, id_khoa=khoa_id).first()
        if not lop_hoc_khoa:
            return jsonify({'message': 'Lớp học không tồn tại trong năm học đã chọn'}), 400
        lop_hoc_khoa_id = lop_hoc_khoa.id
        existing_entries = HocSinhLopHocKhoa.query.filter_by(id_lop_khoa=lop_hoc_khoa_id).all()
        existing_student_ids = {entry.id_hs for entry in existing_entries}

        for student_id in selected_students:
            if student_id not in existing_student_ids:
                # Thêm học sinh vào lớp
                hoc_sinh_lop_hoc_khoa = HocSinhLopHocKhoa(id_hs=student_id, id_lop_khoa=lop_hoc_khoa_id)
                db.session.add(hoc_sinh_lop_hoc_khoa)
            else:
                print("Học sinh đã tồn tại")
        db.session.commit()

        return jsonify({'message': 'Thêm học sinh vào lớp thành công'}), 200
    except Exception as e:
        print(str(e))
        return jsonify({'message': 'Có lỗi xảy ra'}), 500


@app.route('/scores-export')
def scores_export():
    return render_template('scores-export.html')


@app.route('/api/get_scores', methods=['POST'])
def get_scores():
    try:
        data = request.get_json()
        nam_hoc = data.get('nam_hoc')
        hoc_ky = data.get('hoc_ky')
        lop_id = data.get('lop_id')
        mon_hoc_id = data.get('mon_hoc_id')

        # Chuyển đổi học kỳ
        hoc_ky_enum = HocKy.HK1 if hoc_ky == "HK1" else HocKy.HK2

        # Lấy điểm từ database
        scores = dao.get_student_scores(lop_id, mon_hoc_id, hoc_ky_enum)
        return jsonify(scores)

    except Exception as e:
        print(f"Error getting scores: {str(e)}")
        return jsonify({'error': str(e)}), 500


# @app.route('/api/get_bangdiem', methods=['POST'])
# def get_bangdiem():
#     try:
#         data = request.get_json()
#         lop_id = data.get('lop_id')
#         mon_hoc_id = data.get('mon_hoc_id')
#         hoc_ky = data.get('hoc_ky')
#
#         # Chuyển đổi học kỳ string sang enum
#         hoc_ky_enum = HocKy.HK1 if hoc_ky == "HK1" else HocKy.HK2
#
#         # Lấy điểm từ database
#         scores = dao.get_student_scores(lop_id, mon_hoc_id, hoc_ky_enum)
#         return jsonify(scores)
#
#     except Exception as e:
#         print(f"Error in get_bangdiem: {str(e)}")
#         return jsonify({'error': str(e)}), 500
@app.route('/api/get_bangdiem', methods=['POST'])
def get_bangdiem():
    try:
        data = request.json
        nam_hoc = data.get('nam_hoc')
        hoc_ky = data.get('hoc_ky')
        lop_id = data.get('lop_id')
        mon_hoc_id = data.get('mon_hoc_id')

        print(f"Debug - Received data: nam_hoc={nam_hoc}, hoc_ky={hoc_ky}, lop_id={lop_id}, mon_hoc_id={mon_hoc_id}")

        # Kiểm tra môn học tồn tại
        mon_hoc = MonHoc.query.get(mon_hoc_id)
        if not mon_hoc:
            return jsonify({'error': f'Không tìm thấy môn học với ID {mon_hoc_id}'}), 404

        # Lấy khóa học
        khoa = Khoa.query.filter_by(ten_khoa=nam_hoc).first()
        if not khoa:
            return jsonify({'error': 'Không tìm thấy năm học'}), 404

        # Lấy lớp học khóa
        lop_khoa = LopHocKhoa.query.filter_by(
            id_lop=lop_id,
            id_khoa=khoa.id
        ).first()

        if not lop_khoa:
            return jsonify({'error': 'Không tìm thấy lớp trong năm học này'}), 404

        # Lấy danh sách học sinh và điểm
        students = db.session.query(HocSinh) \
            .join(HocSinhLopHocKhoa, HocSinh.id == HocSinhLopHocKhoa.id_hs) \
            .filter(HocSinhLopHocKhoa.id_lop_khoa == lop_khoa.id) \
            .all()

        result = []
        for student in students:
            student_data = {
                'ma_hs': student.id,
                'ho_ten': student.ho_ten,
                'diem_tx': None,
                'diem_gk': None,
                'diem_ck': None
            }

            # Lấy điểm của từng loại
            try:
                diem_tx = Diem.query.filter_by(
                    student_id=student.id,
                    subject_id=mon_hoc_id,
                    loai_diem=LoaiDiem.DIEMTX,
                    hoc_ky=hoc_ky
                ).order_by(Diem.lan.desc()).first()
                student_data['diem_tx'] = diem_tx.diem if diem_tx else None

                diem_gk = Diem.query.filter_by(
                    student_id=student.id,
                    subject_id=mon_hoc_id,
                    loai_diem=LoaiDiem.DIEMGK,
                    hoc_ky=hoc_ky
                ).order_by(Diem.lan.desc()).first()
                student_data['diem_gk'] = diem_gk.diem if diem_gk else None

                diem_ck = Diem.query.filter_by(
                    student_id=student.id,
                    subject_id=mon_hoc_id,
                    loai_diem=LoaiDiem.DIEMCK,
                    hoc_ky=hoc_ky
                ).order_by(Diem.lan.desc()).first()
                student_data['diem_ck'] = diem_ck.diem if diem_ck else None

            except Exception as e:
                print(f"Error getting scores for student {student.id}: {str(e)}")
                # Tiếp tục với học sinh tiếp theo nếu có lỗi
                continue

            result.append(student_data)

        print(f"Debug - Found {len(result)} students")
        return jsonify(result)

    except Exception as e:
        print(f"Error in get_bangdiem: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/get_unassigned_students', methods=['POST'])
def get_unassigned_students():
    try:
        data = request.json
        nam_hoc = data.get('nam_hoc')
        khoi = data.get('khoi')

        # Lấy danh sách học sinh chưa được phân lớp trong năm học này
        khoa = Khoa.query.filter_by(ten_khoa=nam_hoc).first()
        if not khoa:
            return jsonify({'error': 'Không tìm thấy năm học'}), 404

        # Lấy danh sách học sinh đã có lớp
        assigned_students = db.session.query(HocSinh.id) \
            .join(HocSinhLopHocKhoa, HocSinh.id == HocSinhLopHocKhoa.id_hs) \
            .join(LopHocKhoa, HocSinhLopHocKhoa.id_lop_khoa == LopHocKhoa.id) \
            .join(Khoa, LopHocKhoa.id_khoa == Khoa.id) \
            .filter(Khoa.ten_khoa == nam_hoc) \
            .subquery()

        # Lấy học sinh chưa có lớp
        unassigned_students = HocSinh.query \
            .filter(~HocSinh.id.in_(assigned_students)) \
            .all()

        # Lấy danh sách lớp theo khối
        lops = LopHoc.query.filter_by(khoi=khoi).all()

        return jsonify({
            'students': [{
                'id': hs.id,
                'ho_ten': hs.ho_ten,
                'gioi_tinh': hs.gioi_tinh.value,
                'ngay_sinh': hs.ngay_sinh.isoformat(),
                'dia_chi': hs.dia_chi
            } for hs in unassigned_students],
            'lops': [{
                'id': lop.id,
                'ten_lop': lop.ten_lop
            } for lop in lops]
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/assign_student_to_class', methods=['POST'])
def assign_student_to_class():
    try:
        data = request.json
        student_id = data.get('student_id')
        lop_id = data.get('lop_id')
        nam_hoc = data.get('nam_hoc')

        # Kiểm tra sĩ số lớp
        lop = LopHoc.query.get(lop_id)
        khoa = Khoa.query.filter_by(ten_khoa=nam_hoc).first()

        if not lop or not khoa:
            return jsonify({
                'success': False,
                'message': 'Không tìm thấy lớp hoặc năm học'
            }), 404

        lop_khoa = LopHocKhoa.query.filter_by(
            id_lop=lop_id,
            id_khoa=khoa.id
        ).first()

        if not lop_khoa:
            return jsonify({
                'success': False,
                'message': 'Không tìm thấy lớp trong năm học này'
            }), 404

        # Kiểm tra sĩ số
        current_count = HocSinhLopHocKhoa.query \
            .filter_by(id_lop_khoa=lop_khoa.id) \
            .count()

        if current_count >= lop.si_so:
            return jsonify({
                'success': False,
                'message': f'Lớp {lop.ten_lop} đã đủ sĩ số ({lop.si_so} học sinh)'
            })

        # Thêm học sinh vào lớp
        hs_lop_khoa = HocSinhLopHocKhoa(
            id_hs=student_id,
            id_lop_khoa=lop_khoa.id
        )
        db.session.add(hs_lop_khoa)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Phân lớp thành công'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# Xử lý vẽ biểu đồ
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


@app.route('/api/student-counts')
def api_student_counts():
    data = dao.get_students_count_per_class()
    return jsonify(data)


@app.route('/api/gender-ratio', methods=['GET'])
def gender_ratio_api():
    try:
        classes = get_all_lop()  # Lấy tất cả các lớp
        data = []
        for cls in classes:
            ratio = dao.get_gender_ratio_by_class(cls['id'])
            data.append({
                "ten_lop": cls['ten_lop'],
                "nam": ratio['nam'],
                "nu": ratio['nu'],
                "tong": ratio['tong']
            })
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500





@app.route('/api/report', methods=['GET'])
def get_report():
    subject_id = request.args.get('subject_id')  # ID môn học
    semester = request.args.get('semester')  # Học kỳ (e.g., 'HK1', 'HK2')
    year = request.args.get('year')  # Năm học

    # Gọi hàm trong DAO
    report_data = dao.get_class_report(subject_id, semester, year)
    return jsonify(report_data)

@app.route('/api/grade-distribution', methods=['GET'])
def grade_distribution_api():
    try:
        print("\n=== ĐANG GỌI API GRADE-DISTRIBUTION ===")
        data = dao.get_grade_distribution()
        print(f"Số lượng dữ liệu trả về: {len(data)}")
        print("Dữ liệu:", data)
        return jsonify(data)
    except Exception as e:
        print(f"\n=== LỖI TRONG API GRADE-DISTRIBUTION ===")
        print(f"Loại lỗi: {e.__class__.__name__}")
        print(f"Chi tiết: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/check-scores', methods=['GET'])
def check_scores_api():
    try:
        has_scores = dao.check_diem_data()
        return jsonify({
            'has_scores': has_scores,
            'message': 'Có dữ liệu điểm trong CSDL' if has_scores else 'Không có dữ liệu điểm'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
if __name__ == "__main__":
    with app.app_context():
        from app import admin

        app.run(debug=True)
