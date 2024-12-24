import hashlib
from sqlalchemy import inspect, func
import random
import unidecode
from app import db, app
from app.models import (User, HocSinh, UserRole,
                        GioiTinh, MonHoc, LopHoc,
                        Khoa, Diem, KetQuaHocTap,
                        LopHocKhoa, HocSinhLopHocKhoa,
                        GiaoVienMonHoc, GiaoVienMonHocLopHocKhoa,
                        HocKy, Khoi, LoaiDiem)


def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    user = User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password))
    return user.first()


def get_user_by_id(id):
    return User.query.get(id)


def random_id_lop():
    x = db.session.query(LopHoc.id).all()
    y = random.choice(x)
    y_int = int(y[0])

    return y_int


def add_stu(ho_ten, gioi_tinh, ngay_sinh, dia_chi, email, so_dien_thoai):
    hs = HocSinh(ho_ten=ho_ten,
                 gioi_tinh=gioi_tinh,
                 ngay_sinh=ngay_sinh,
                 dia_chi=dia_chi,
                 so_dien_thoai=so_dien_thoai,
                 email=email)

    db.session.add(hs)
    db.session.commit()


def get_lophoc_by_khoi(ten_khoi):
    list_ten_lop = [lop.ten_lop for lop in LopHoc.query.filter(LopHoc.khoi == ten_khoi).all()]
    return list_ten_lop


def get_nam_hoc():
    ten_khoa = db.session.query(Khoa.ten_khoa).distinct().all()
    khoa = [row[0] for row in ten_khoa]
    print(khoa)
    return khoa


def get_khoi():
    return list(Khoi)


def get_id_khoa_by_ten_khoa(ten_khoa):
    id_khoa = db.session.query(Khoa.id).filter(Khoa.ten_khoa == ten_khoa).all()
    if id_khoa:
        return [khoa.id for khoa in id_khoa]
    return []


def get_id_lop_by_ten_lop(ten_lop):
    id_lop = db.session.query(LopHoc.id).filter(LopHoc.ten_lop == ten_lop).all()
    if id_lop:  # Kiểm tra danh sách có rỗng hay không
        return id_lop[0][0]
    else:
        return None  # Hoặc trả về một giá trị mặc định khác


def get_id_lopkhoa_by_id_lop_khoa(id_khoa, id_lop):
    list_id_lop_khoa = []
    for khoa in id_khoa:
        id_lop_khoa = LopHocKhoa.query.filter_by(id_khoa=khoa, id_lop=id_lop).all()
        list_id_lop_khoa.extend([lop_khoa.id for lop_khoa in id_lop_khoa])
    return list_id_lop_khoa


def get_id_lop_khoa(id_khoa, id_lop):
    id_lopkhoa = LopHocKhoa.query.filter_by(id_khoa=id_khoa, id_lop=id_lop).all()
    return int(id_lopkhoa[0].id)


def get_list_id_hs_by_id_lopkhoa(id_lopkhoa):
    if isinstance(id_lopkhoa, int):  # Nếu chỉ có một ID lớp khoa
        id_lopkhoa = [id_lopkhoa]

    list_id_hs = HocSinhLopHocKhoa.query.filter(HocSinhLopHocKhoa.id_lop_khoa.in_(id_lopkhoa)).all()

    return [item.id_hs for item in list_id_hs]


def get_hs_info_by_id_hs(id_hs):
    hocsinh_list = HocSinh.query.filter(HocSinh.id.in_(id_hs)).all()
    hoc_sinh_info = [
        {
            "ho_ten": hs.ho_ten,
            "gioi_tinh": hs.gioi_tinh.value,
            "nam_sinh": hs.ngay_sinh.year,
            "dia_chi": hs.dia_chi
        }
        for hs in hocsinh_list
    ]
    return hoc_sinh_info


def get_all_lop():
    lop_hoc_list = LopHoc.query.with_entities(LopHoc.id, LopHoc.ten_lop).all()
    lophoc = [{
        "id": l.id,
        "ten_lop": l.ten_lop
    }
        for l in lop_hoc_list
    ]
    return lophoc


def get_khoa_id(ten_nam, hoc_ky):
    """
    Lấy ID của khóa dựa vào tên năm và kỳ học.

    :param ten_nam: Tên năm của khóa (ví dụ: "2024-2025")
    :param hoc_ky: Giá trị Enum đại diện cho học kỳ (ví dụ: HocKy.HK1)
    :return: ID của khóa hoặc None nếu không tìm thấy
    """
    try:
        khoa = db.session.query(Khoa.id).filter(
            Khoa.ten_khoa == ten_nam,
            Khoa.hoc_ky == hoc_ky
        ).first()

        return khoa[0] if khoa else None
    except Exception as e:
        print(f"Lỗi khi lấy ID của khóa: {e}")
        return None


# lấy danh sách môn học
def get_all_subjects():
    """
    Lấy danh sách tất cả các môn học từ cơ sở dữ liệu.

    Returns:
        List[dict]: Danh sách môn học dưới dạng dictionary, mỗi phần tử có cấu trúc:
                    {
                        'id': int,
                        'ten_mon_hoc': str
                    }
    """
    subjects = MonHoc.query.all()
    result = [{'id': subject.id, 'ten_mon_hoc': subject.ten_mon_hoc} for subject in subjects]
    return result


def get_monhoc_by_lopkhoa(id_lop_khoa):
    """
    Lấy danh sách môn học của một lớp trong một khóa học
    """
    try:
        # Trước tiên thử lấy các môn học đã được phân công
        monhoc_list = (db.session.query(MonHoc)
                       .join(GiaoVienMonHocLopHocKhoa, MonHoc.id == GiaoVienMonHocLopHocKhoa.id_mon_hoc)
                       .filter(GiaoVienMonHocLopHocKhoa.id_lop_khoa == id_lop_khoa)
                       .distinct()
                       .all())

        # Nếu chưa có môn học nào được phân công, lấy tất cả môn học
        if not monhoc_list:
            monhoc_list = MonHoc.query.all()

        return [{
            'id': mon.id,
            'ten_mon_hoc': mon.ten_mon_hoc
        } for mon in monhoc_list]
    except Exception as e:
        print(f"Error in get_monhoc_by_lopkhoa: {str(e)}")
        return []


def get_diem_id(id_hs, id_mon_hoc):
    """
    Lấy ID của điểm dựa vào ID học sinh và ID môn học.

    Args:
        id_hs (int): ID của học sinh
        id_mon_hoc (int): ID của môn học

    Returns:
        int: ID của điểm hoặc None nếu không tìm thấy
    """
    try:
        diem = Diem.query.filter_by(id_hs=id_hs, id_mon_hoc=id_mon_hoc).first()
        return diem.id if diem else None
    except Exception as e:
        print(f"Lỗi khi lấy ID điểm: {e}")
        return None


def get_monhoc_by_lopkhoa(id_lop_khoa):
    """
    Lấy danh sách môn học của một lớp trong một khóa học
    """
    try:
        print(f"Đang tìm môn học cho lớp khóa ID: {id_lop_khoa}")

        # Kiểm tra phân công giáo viên
        gv_monhoc = (db.session.query(GiaoVienMonHocLopHocKhoa)
                     .filter(GiaoVienMonHocLopHocKhoa.id_lop_khoa == id_lop_khoa)
                     .all())

        print(f"Số lượng phân công giáo viên: {len(gv_monhoc)}")

        if gv_monhoc:
            # Nếu có phân công, lấy môn học theo phân công
            monhoc_list = (db.session.query(MonHoc)
                           .join(GiaoVienMonHocLopHocKhoa, MonHoc.id == GiaoVienMonHocLopHocKhoa.id_mon_hoc)
                           .filter(GiaoVienMonHocLopHocKhoa.id_lop_khoa == id_lop_khoa)
                           .distinct()
                           .all())
        else:
            # Nếu chưa có phân công, lấy tất cả môn học
            print("Không có phân công giáo viên, lấy tất cả môn học")
            monhoc_list = MonHoc.query.all()

        result = [{
            'id': mon.id,
            'ten_mon_hoc': mon.ten_mon_hoc
        } for mon in monhoc_list]

        print(f"Danh sách môn học: {result}")
        return result

    except Exception as e:
        print(f"Lỗi trong get_monhoc_by_lopkhoa: {str(e)}")
        return []


def get_students_with_scores(id_lopkhoa, mon_hoc_id, hoc_ky):
    """
    Lấy danh sách học sinh và điểm của họ cho một môn học cụ thể
    """
    try:
        # Lấy danh sách học sinh trong lớp
        students = (db.session.query(HocSinh)
                    .join(HocSinhLopHocKhoa, HocSinh.id == HocSinhLopHocKhoa.id_hs)
                    .filter(HocSinhLopHocKhoa.id_lop_khoa == id_lopkhoa)
                    .all())

        result = []
        for student in students:
            # Lấy điểm của học sinh cho môn học này
            diem_15 = (Diem.query
                       .filter_by(student_id=student.id,
                                  subject_id=mon_hoc_id,
                                  loai_diem=LoaiDiem.DIEMTX,
                                  hoc_ky=hoc_ky)
                       .first())

            diem_1t = (Diem.query
                       .filter_by(student_id=student.id,
                                  subject_id=mon_hoc_id,
                                  loai_diem=LoaiDiem.DIEMGK,
                                  hoc_ky=hoc_ky)
                       .first())

            diem_ck = (Diem.query
                       .filter_by(student_id=student.id,
                                  subject_id=mon_hoc_id,
                                  loai_diem=LoaiDiem.DIEMCK,
                                  hoc_ky=hoc_ky)
                       .first())

            student_data = {
                'id': student.id,
                'ho_ten': student.ho_ten,
                'diem_tx': diem_15.diem if diem_15 else None,
                'diem_gk': diem_1t.diem if diem_1t else None,
                'diem_ck': diem_ck.diem if diem_ck else None
            }
            result.append(student_data)

        return result

    except Exception as e:
        print(f"Error in get_students_with_scores: {str(e)}")
        return []


def save_student_scores(scores, mon_hoc_id, hoc_ky):
    """
    Lưu điểm của học sinh vào bảng Diem
    """
    try:
        print(f"Đang lưu điểm: {scores}")
        for score in scores:
            student_id = score.get('student_id')
            diem_tx = score.get('diem_tx')
            diem_gk = score.get('diem_gk')
            diem_ck = score.get('diem_ck')

            # Kiểm tra và lưu từng loại điểm
            if diem_tx is not None:
                save_or_update_diem(student_id, mon_hoc_id, diem_tx, LoaiDiem.DIEMTX, hoc_ky)

            if diem_gk is not None:
                save_or_update_diem(student_id, mon_hoc_id, diem_gk, LoaiDiem.DIEMGK, hoc_ky)

            if diem_ck is not None:
                save_or_update_diem(student_id, mon_hoc_id, diem_ck, LoaiDiem.DIEMCK, hoc_ky)

        db.session.commit()
        print("Lưu điểm thành công")
        return True

    except Exception as e:
        print(f"Lỗi khi lưu điểm: {str(e)}")
        db.session.rollback()
        raise e


def save_diem(student_id, subject_id, diem_value, loai_diem, hoc_ky):
    """
    Lưu điểm mới vào database
    """
    try:
        # Kiểm tra điểm đã tồn tại
        existing_diem = Diem.query.filter_by(
            student_id=student_id,
            subject_id=subject_id,
            loai_diem=loai_diem,
            hoc_ky=hoc_ky
        ).order_by(Diem.lan.desc()).first()

        # Xác định lần nhập điểm
        lan = 1 if not existing_diem else existing_diem.lan + 1

        # Tạo bản ghi điểm mới
        new_diem = Diem(
            student_id=student_id,
            subject_id=subject_id,
            diem=diem_value,
            lan=lan,
            loai_diem=loai_diem,
            hoc_ky=hoc_ky
        )

        print(f"Saving score: Student={student_id}, Subject={subject_id}, "
              f"Score={diem_value}, Type={loai_diem}, Semester={hoc_ky}")  # Debug log

        db.session.add(new_diem)
        db.session.commit()

        return True

    except Exception as e:
        print(f"Error in save_diem: {str(e)}")  # Debug log
        db.session.rollback()
        raise e


def save_or_update_diem(student_id, subject_id, diem_value, loai_diem, hoc_ky):
    """
    Lưu hoặc cập nhật điểm trong bảng Diem
    """
    try:
        # Tìm điểm đã tồn tại với lần cao nhất
        existing_diem = (Diem.query
                         .filter_by(
            student_id=student_id,
            subject_id=subject_id,
            loai_diem=loai_diem,
            hoc_ky=hoc_ky)
                         .order_by(Diem.lan.desc())
                         .first())

        if existing_diem:
            # Tạo bản ghi mới với lần tăng thêm 1
            new_lan = existing_diem.lan + 1
            new_diem = Diem(
                student_id=student_id,
                subject_id=subject_id,
                diem=diem_value,
                lan=new_lan,
                loai_diem=loai_diem,
                hoc_ky=hoc_ky
            )
            db.session.add(new_diem)
            print(f"Thêm điểm mới lần {new_lan}: Học sinh {student_id}, Môn {subject_id}, "
                  f"Loại {loai_diem}, Điểm {diem_value}")
        else:
            # Tạo mới điểm với lần = 1
            new_diem = Diem(
                student_id=student_id,
                subject_id=subject_id,
                diem=diem_value,
                lan=1,
                loai_diem=loai_diem,
                hoc_ky=hoc_ky
            )
            db.session.add(new_diem)
            print(f"Thêm điểm mới lần 1: Học sinh {student_id}, Môn {subject_id}, "
                  f"Loại {loai_diem}, Điểm {diem_value}")

    except Exception as e:
        print(f"Lỗi khi lưu/cập nhật điểm: {str(e)}")
        raise e


def get_student_scores(lop_id, mon_hoc_id, hoc_ky):
    """
    Lấy điểm của học sinh theo lớp, môn học và học kỳ
    """
    try:
        # Lấy danh sách học sinh trong lớp
        students = db.session.query(HocSinh) \
            .join(HocSinhLopHocKhoa, HocSinh.id == HocSinhLopHocKhoa.id_hs) \
            .join(LopHocKhoa, HocSinhLopHocKhoa.id_lop_khoa == LopHocKhoa.id) \
            .filter(LopHocKhoa.id_lop == lop_id) \
            .all()

        result = []
        for student in students:
            # Lấy điểm của từng loại
            diem_tx = Diem.query.filter_by(
                student_id=student.id,
                subject_id=mon_hoc_id,
                loai_diem=LoaiDiem.DIEMTX,
                hoc_ky=hoc_ky
            ).order_by(Diem.lan.desc()).first()

            diem_gk = Diem.query.filter_by(
                student_id=student.id,
                subject_id=mon_hoc_id,
                loai_diem=LoaiDiem.DIEMGK,
                hoc_ky=hoc_ky
            ).order_by(Diem.lan.desc()).first()

            diem_ck = Diem.query.filter_by(
                student_id=student.id,
                subject_id=mon_hoc_id,
                loai_diem=LoaiDiem.DIEMCK,
                hoc_ky=hoc_ky
            ).order_by(Diem.lan.desc()).first()

            result.append({
                'ma_hs': student.id,
                'ho_ten': student.ho_ten,
                'diem_tx': diem_tx.diem if diem_tx else None,
                'diem_gk': diem_gk.diem if diem_gk else None,
                'diem_ck': diem_ck.diem if diem_ck else None
            })

        return result

    except Exception as e:
        print(f"Error in get_student_scores: {str(e)}")
        raise e


# vẽ biểu đồ
def get_students_count_per_class():
    results = (
        db.session.query(
            LopHoc.ten_lop,
            db.func.count(HocSinhLopHocKhoa.id_hs).label('total_students')
        )
        .join(LopHocKhoa, LopHoc.id == LopHocKhoa.id_lop)
        .join(HocSinhLopHocKhoa, LopHocKhoa.id == HocSinhLopHocKhoa.id_lop_khoa)
        .group_by(LopHoc.ten_lop)
        .all()
    )

    return [{"ten_lop": r.ten_lop, "total_students": r.total_students} for r in results]


def get_gender_ratio_by_class(class_id):
    results = (
        db.session.query(
            HocSinh.gioi_tinh,
            db.func.count(HocSinh.id).label('count')
        )
        .join(HocSinhLopHocKhoa, HocSinh.id == HocSinhLopHocKhoa.id_hs)
        .join(LopHocKhoa, HocSinhLopHocKhoa.id_lop_khoa == LopHocKhoa.id)
        .filter(LopHocKhoa.id_lop == class_id)
        .group_by(HocSinh.gioi_tinh)
        .all()
    )

    # Mặc định số lượng là 0 nếu không có dữ liệu
    gender_counts = {gender.value: count for gender, count in results}
    total_students = sum(gender_counts.values())

    return {
        "nam": gender_counts.get("Nam", 0),
        "nu": gender_counts.get("Nữ", 0),
        "tong": total_students
    }


def get_grade_distribution():
    try:
        print("\n=== BẮT ĐẦU LẤY ĐIỂM TRUNG BÌNH TỪNG LỚP ===")

        # Lấy tất cả các lớp trước
        all_classes = LopHoc.query.all()
        data = []

        for lop in all_classes:
            print(f"\nĐang xử lý lớp: {lop.ten_lop}")

            # Lấy điểm trung bình của lớp
            avg_score = db.session.query(
                func.avg(Diem.diem).label('diem_trung_binh')
            ).join(
                HocSinhLopHocKhoa, HocSinhLopHocKhoa.id_hs == Diem.student_id
            ).join(
                LopHocKhoa, LopHocKhoa.id == HocSinhLopHocKhoa.id_lop_khoa
            ).filter(
                LopHocKhoa.id_lop == lop.id
            ).scalar()

            # Thêm vào kết quả kể cả khi chưa có điểm
            item = {
                'ten_lop': lop.ten_lop,
                'diem_trung_binh': round(float(avg_score), 2) if avg_score is not None else 0
            }
            data.append(item)
            print(f"Lớp {lop.ten_lop}: {item['diem_trung_binh']}")

        print(f"\nTổng số lớp: {len(data)}")
        return data

    except Exception as e:
        print(f"\n=== LỖI: {str(e)} ===")
        import traceback
        print(traceback.format_exc())
        return []
def check_diem_data():
    try:
        # Đếm tổng số điểm
        total_scores = db.session.query(Diem).count()
        print(f"\nTổng số điểm trong CSDL: {total_scores}")

        # Lấy mẫu một vài điểm
        sample_scores = Diem.query.limit(5).all()
        print("\nMẫu điểm:")
        for score in sample_scores:
            print(f"Học sinh {score.student_id}: {score.diem} ({score.loai_diem.value})")

        return total_scores > 0
    except Exception as e:
        print(f"Lỗi khi kiểm tra dữ liệu điểm: {str(e)}")
        return False

if __name__ == "__main__":
    with app.app_context():
        pass
        # ten_nam = "2024-2025"
        # hoc_ky = "HK1"
        # id_lop = 1
        #
        # khoa_id = get_khoa_id(ten_nam, hoc_ky)
        # print(khoa_id)
        # print(type(khoa_id))
        #
        # id_lop_khoa= get_id_lop_khoa(khoa_id, id_lop)
        # print(type(id_lop_khoa))
        # print(f"id lop khoa:{id_lop_khoa}")
        #
        # id_hocsinh = get_list_id_hs_by_id_lopkhoa(id_lop_khoa)
        # print(f"id hoc sinh: {id_hocsinh}")
        #
        # subjects = get_all_subjects()
        # print(subjects)

        # test lấy thuộc tính điểm

        # print(get_class_report())
