import hashlib
import random
import unidecode
from flask import jsonify

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
    return id_lop[0][0]


def get_id_lopkhoa_by_id_lop_id_khoa(id_khoa_list, id_lop):
    # Truy vấn tất cả các LopHocKhoa có id_khoa trong danh sách và id_lop tương ứng
    id_lop_khoa_list = (
        LopHocKhoa.query
        .filter(LopHocKhoa.id_khoa.in_(id_khoa_list), LopHocKhoa.id_lop == id_lop)
        .with_entities(LopHocKhoa.id)  # Chỉ lấy trường id
        .all()
    )
    # Trả về danh sách các id
    return [item[0] for item in id_lop_khoa_list]


def get_list_id_hs_by_id_lopkhoa(id_lopkhoa):
    if isinstance(id_lopkhoa, int):  # Nếu chỉ có một ID lớp khoa
        id_lopkhoa = [id_lopkhoa]

    list_id_hs = HocSinhLopHocKhoa.query.filter(HocSinhLopHocKhoa.id_lop_khoa.in_(id_lopkhoa)).all()

    return [item.id_hs for item in list_id_hs]


def get_hs_info_by_id_hs(id_hs):
    hocsinh_list = HocSinh.query.filter(HocSinh.id.in_(id_hs)).all()
    hoc_sinh_info = [
        {
            "id": hs.id,
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


if __name__ == "__main__":
    with app.app_context():
        nam_hoc = '2023-2024'
        lop = '10A1'

        print(get_id_khoa_by_ten_khoa(nam_hoc))
        id_khoa = get_id_khoa_by_ten_khoa(nam_hoc)
        print(get_id_lop_by_ten_lop(lop))
        id_lop = get_id_lop_by_ten_lop(lop)
        print(get_id_lopkhoa_by_id_lop_id_khoa(id_khoa, id_lop))
