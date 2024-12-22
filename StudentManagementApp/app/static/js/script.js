function addLopToDropdown() {
    let ten_khoi = document.getElementById("khoi").value;
    let nam_hoc = document.getElementById("namHoc").value;
    let lop = document.getElementById('lop');
    lop.innerHTML = '<option value="">-- Chọn lớp --</option>';

    fetch('/api/get_lop_by_khoi', {
        method: "POST",
        body: JSON.stringify({
            nam_hoc: nam_hoc,
            ten_khoi: ten_khoi
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(data => {
        data.forEach(item => {
            let option = document.createElement('option');
            option.value = item.ten_lop;
            option.textContent = item.ten_lop;
            lop.appendChild(option);
        });
    }).catch(error => {
        console.error('Lỗi khi lấy danh sách lớp:', error);
        alert('Đã xảy ra lỗi khi lấy danh sách lớp!');
    });
}

function changeTitleTable() {
    let lop = document.getElementById('lop').value;
    let title = document.getElementById('title')
    title.innerHTML = '<h3 class="text-center">Danh sách học sinh lớp ' + lop + '</h3>'
}

function loadHocsinh() {
    let ten_khoi = document.getElementById("khoi").value;
    let nam_hoc = document.getElementById("namHoc").value;
    let ten_lop = document.getElementById("lop").value;

    fetch('/api/get_hocsinh', {
        method: "POST",
        body: JSON.stringify({
            nam_hoc: nam_hoc,
            ten_khoi: ten_khoi,
            ten_lop: ten_lop
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(res => res.json())
        .then(data => {
            const {hs, lop} = data;

            // Xóa nội dung cũ
            let tableBody = document.getElementById("hocsinh_body");
            tableBody.innerHTML = "";

            let soThuTu = 0;

            // Lặp qua danh sách học sinh
            hs.forEach(h => {
                soThuTu++;
                const row = document.createElement("tr");

                // Tạo dropdown cho danh sách lớp và chọn lớp mặc định của học sinh
                let dropdownHTML = `<select class="lop-dropdown form-select">`;
                lop.forEach(l => {
                    dropdownHTML += `<option value="${l.id}" ${h.id_lop === l.id ? 'selected' : ''}>${l.ten_lop}</option>`;
                    if (ten_lop === lop.ten_lop){
                    }
                    dropdownHTML += `<option value="${l.id}" ${h.id_lop === l.id ? 'selected' : ''}>${l.ten_lop}</option>`;
                });
                dropdownHTML += `</select>`;

                // Thêm thông tin học sinh và dropdown lớp
                row.innerHTML = `
                <td>${soThuTu}</td>
                <td>${h.ho_ten}</td>
                <td>${h.gioi_tinh}</td>
                <td>${h.nam_sinh}</td>
                <td>${h.dia_chi}</td>
                <td>${dropdownHTML}</td>
            `;
                tableBody.appendChild(row);
            });
        });
}


// function changeLopOfHocSinh() {
//     let id_lop = document.getElementsByClassName("lop-dropdown").value;
//     let nam_hoc = document.getElementById("namHoc").value;
//
//     fetch('/api/change-lop-hs', {
//         method: "POST",
//         body: JSON.stringify({
//             nam_hoc: nam_hoc,
//             id_lop: id_lop
//         }),
//         headers: {
//             'Content-Type': 'application/json'
//         }
//     }).then(res => res.json()).then(data => {
//
//
//     });
// }


