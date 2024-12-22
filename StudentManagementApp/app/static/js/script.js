function addLopToDropdown() {
    let ten_khoi = document.getElementById("khoi").value;
    let nam_hoc = document.getElementById("namHoc").value;
    let lop = document.getElementById('lop');
    lop.innerHTML = '<option value="">-- Chọn lớp --</option>';

    fetch('/api/get_lop_by_khoi', {
        method: "POST", body: JSON.stringify({
            nam_hoc: nam_hoc, ten_khoi: ten_khoi
        }), headers: {
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
    let nam_hoc = document.getElementById("namHoc").value;
    let ten_lop = document.getElementById("lop").value;
    let tableBody = document.getElementById("hocsinh_body");
    tableBody.innerHTML = "";
    fetch('/api/get_hocsinh', {
        method: "POST", body: JSON.stringify({
            nam_hoc: nam_hoc, ten_lop: ten_lop
        }), headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(data => {
        let soThuTu = 0;
        data.hs.forEach(h => {
            let dropdown = `<select class="dropdown-lop form-select">`;
            data.lop.forEach(l => {
                dropdown += `<option value="${l.id}" ${l.ten_lop === ten_lop ? 'selected' : ''}>${l.ten_lop}</option>`;
            });
            dropdown += `</select>`;

            soThuTu++;

            // let row = document.createElement("tr");
            tableBody.innerHTML += `
                <tr id="${h.id}">
                    <td>${soThuTu}</td>
                    <td>${h.ho_ten}</td>
                    <td>${h.gioi_tinh}</td>
                    <td>${h.nam_sinh}</td>
                    <td>${h.dia_chi}</td>
                    <td>
                        ${dropdown}
                    </td>
                </tr>
                `;
        });
    });
}


function changeLopOfHocSinh() {
    document.addEventListener('change', function (event) {
        // Kiểm tra xem sự kiện xảy ra trên phần tử có class "dropdown-lop"
        if (event.target && event.target.classList.contains('dropdown-lop')) {
            const dropdown = event.target; // Dropdown bị thay đổi
            const tr = dropdown.closest('tr'); // Lấy thẻ <tr> chứa dropdown
            const trId = tr ? tr.id : null; // ID của thẻ <tr>
            const dropdownValue = dropdown.value; // Value của dropdown

            // Tạo danh sách kết quả
            let hocSinhLopMoi = {
                id_hs: trId,
                id_lop: dropdownValue
            };
        }
    });
    let nam_hoc = document.getElementById("namHoc").value;
    let ten_lop_cu = document.getElementById("lop").value;

    fetch('/api/update-lop-hs', {
        method: "POST", body: JSON.stringify({
            nam_hoc: nam_hoc,
            ten_lop_cu: ten_lop_cu,
            lop_moi: hocSinhLopMoi
        }), headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(data => {
        alert(data.message);

    });
}
