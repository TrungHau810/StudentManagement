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

//function scores-input
const namHocSelect = document.getElementById('namHoc');
const hocKySelect = document.getElementById('hocKy');
const lopSelect = document.getElementById('lop');
const monHocSelect = document.getElementById('monHoc');
const subjectHeaders = document.getElementById('subjectHeaders');
const studentScores = document.getElementById('studentScores');
const saveButton = document.getElementById('saveScores');




document.getElementById('monHoc').addEventListener('change', async function() {
    const monHocId = this.value;
    const lopId = lopSelect.value;
    const hocKy = hocKySelect.value;
    const namHoc = namHocSelect.value;

    if (!monHocId || !lopId || !hocKy || !namHoc) {
        alert('Vui lòng chọn đầy đủ thông tin!');
        return;
    }

    try {
        const response = await fetch('/api/get_bangdiem', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mon_hoc_id: monHocId,
                lop_id: lopId,
                hoc_ky: hocKy,
                nam_hoc: namHoc
            })
        });

        const data = await response.json();
        renderBangDiem(data);
    } catch (error) {
        console.error('Error fetching bảng điểm:', error);
        alert('Có lỗi khi tải bảng điểm');
    }
});

async function fetchNamHoc() {
    try {
        const response = await fetch('/api/get_namhoc');
        const data = await response.json();
        namHocSelect.innerHTML = '<option value="">-- Chọn năm học --</option>';
        data.forEach(nh => {
            namHocSelect.innerHTML += `<option value="${nh}">${nh}</option>`;
        });
    } catch (error) {
        console.error('Error fetching năm học:', error);
    }
}

// Khi chọn năm học
namHocSelect.addEventListener('change', async () => {
    const namHoc = namHocSelect.value;
    if (!namHoc) return;

    try {
        const response = await fetch('/api/get_hocky_by_namhoc', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nam_hoc: namHoc })
        });
        const data = await response.json();

        hocKySelect.innerHTML = '<option value="">-- Chọn học kỳ --</option>';
        data.hoc_ky.forEach(hk => {
            hocKySelect.innerHTML += `<option value="${hk.id}">${hk.ten}</option>`;
        });
        hocKySelect.disabled = false;
        lopSelect.disabled = true;
        monHocSelect.disabled = true; // Disable môn học
        clearTable();
    } catch (error) {
        console.error('Error fetching học kỳ:', error);
    }
});

// Khi chọn học kỳ
hocKySelect.addEventListener('change', async () => {
    const hocKy = hocKySelect.value;
    const namHoc = namHocSelect.value;
    if (!hocKy || !namHoc) return;

    try {
        const response = await fetch('/api/get_lop_by_namhoc_hocky', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nam_hoc: namHoc, hoc_ky: hocKy })
        });
        const data = await response.json();

        lopSelect.innerHTML = '<option value="">-- Chọn lớp --</option>';
        data.lop.forEach(lop => {
            lopSelect.innerHTML += `<option value="${lop.id}">${lop.ten}</option>`;
        });
        lopSelect.disabled = false;
        monHocSelect.disabled = true;
        clearTable();
    } catch (error) {
        console.error('Error fetching lớp:', error);
    }
});

// Khi chọn lớp
lopSelect.addEventListener('change', async function() {
    const lopId = this.value;
    const hocKy = hocKySelect.value;
    const namHoc = namHocSelect.value;
    const monHocSelect = document.getElementById('monHoc');

    // Reset và disable môn học select
    monHocSelect.innerHTML = '<option value="">-- Chọn môn học --</option>';
    monHocSelect.disabled = true;

    if (!lopId || !hocKy || !namHoc) {
        clearTable();
        return;
    }

    try {
        console.log('Fetching môn học with:', { lopId, hocKy, namHoc });
        const response = await fetch('/api/get_monhoc_by_lop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                lop_id: lopId,
                hoc_ky: hocKy,
                nam_hoc: namHoc
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Received môn học data:', data);

        if (data.error) {
            throw new Error(data.error);
        }


        monHocSelect.innerHTML = '<option value="">-- Chọn môn học --</option>';
        data.mon_hoc.forEach(mon => {
            monHocSelect.innerHTML += `<option value="${mon.id}">${mon.ten_mon_hoc}</option>`;
        });
        monHocSelect.disabled = false;
        clearTable();
    } catch (error) {
        console.error('Error fetching môn học:', error);
        alert('Có lỗi khi tải danh sách môn học: ' + error.message);
    }
});
// Sửa lại event listener của môn học
monHocSelect.addEventListener('change', async function() {
    const monHocId = this.value;
    const lopId = lopSelect.value;
    const hocKy = hocKySelect.value;
    const namHoc = namHocSelect.value;

    if (!monHocId || !lopId || !hocKy || !namHoc) {
        clearTable();
        return;
    }

    try {
        const response = await fetch('/api/get_students_and_subjects', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                lop_id: lopId,
                hocKy: hocKy,
                namHoc: namHoc,
                monHocId: monHocId
            })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        // Hiển thị bảng điểm
        document.getElementById('classContent').style.display = 'block';

        // Headers
        subjectHeaders.innerHTML = `
            <th>STT</th>
            <th>Mã học sinh</th>
            <th>Họ và tên</th>
            <th>Điểm 15 phút</th>
            <th>Điểm 1 tiết</th>
            <th>Điểm cuối kỳ</th>
        `;

        // Students
        studentScores.innerHTML = data.students.map((student, index) => `
            <tr>
                <td>${index + 1}</td>
                <td>${student.id}</td>
                <td>${student.ho_ten}</td>
                <td><input type="number" min="0" max="10" step="0.1" class="form-control score-input"
                    data-student-id="${student.id}" data-type="DIEMTX"
                    value="${student.diem_tx || ''}"></td>
                <td><input type="number" min="0" max="10" step="0.1" class="form-control score-input"
                    data-student-id="${student.id}" data-type="DIEMGK"
                    value="${student.diem_gk || ''}"></td>
                <td><input type="number" min="0" max="10" step="0.1" class="form-control score-input"
                    data-student-id="${student.id}" data-type="DIEMCK"
                    value="${student.diem_ck || ''}"></td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error:', error);
        alert('Có lỗi khi tải dữ liệu học sinh');
    }
});

// Sửa lại hàm renderBangDiem để xử lý dữ liệu an toàn hơn
function renderBangDiem(data) {
    const students = data.students || [];

    if (students.length === 0) {
        subjectHeaders.innerHTML = '<th colspan="5" class="text-center">Không có dữ liệu học sinh</th>';
        studentScores.innerHTML = '';
        return;
    }

    // Headers
    subjectHeaders.innerHTML = `
        <th>STT</th>
        <th>Họ và tên</th>
        <th>Điểm 15 phút</th>
        <th>Điểm 1 tiết</th>
        <th>Điểm cuối kỳ</th>
    `;

    // Students
    studentScores.innerHTML = students.map((student, index) => `
        <tr>
            <td>${index + 1}</td>
            <td>${student.ho_ten || 'N/A'}</td>
            <td><input type="number" min="0" max="10" step="0.1" class="form-control score-input"
                data-student-id="${student.id}" data-type="DIEMTX"
                value="${student.diem_tx || ''}"
                ${student.id ? '' : 'disabled'}></td>
            <td><input type="number" min="0" max="10" step="0.1" class="form-control score-input"
                data-student-id="${student.id}" data-type="DIEMGK"
                value="${student.diem_gk || ''}"
                ${student.id ? '' : 'disabled'}></td>
            <td><input type="number" min="0" max="10" step="0.1" class="form-control score-input"
                data-student-id="${student.id}" data-type="DIEMCK"
                value="${student.diem_ck || ''}"
                ${student.id ? '' : 'disabled'}></td>
        </tr>
    `).join('');
}

document.getElementById('saveScores').addEventListener('click', async function() {
    try {
        const scores = [];
        const rows = document.querySelectorAll('#studentScores tr');

        rows.forEach(row => {
            const studentId = row.querySelector('td:nth-child(2)').textContent;
            const diemTX = row.querySelector('input[data-type="DIEMTX"]').value;
            const diemGK = row.querySelector('input[data-type="DIEMGK"]').value;
            const diemCK = row.querySelector('input[data-type="DIEMCK"]').value;

            scores.push({
                student_id: parseInt(studentId),
                diem_tx: diemTX ? parseFloat(diemTX) : null,
                diem_gk: diemGK ? parseFloat(diemGK) : null,
                diem_ck: diemCK ? parseFloat(diemCK) : null
            });
        });

        const monHocId = document.getElementById('monHoc').value;
        const hocKy = document.getElementById('hocKy').value;

        const response = await fetch('/api/save_scores', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                scores: scores,
                mon_hoc_id: monHocId,
                hoc_ky: hocKy
            })
        });

        const result = await response.json();

        if (response.ok) {
            alert('Lưu điểm thành công!');
        } else {
            throw new Error(result.error || 'Có lỗi xảy ra khi lưu điểm');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Lỗi: ' + error.message);
    }
});

// Hiển thị bảng danh sách học sinh
//function renderStudentTable(students) {
//    if (!Array.isArray(students) || students.length === 0) {
//        subjectHeaders.innerHTML = '<th colspan="8" class="text-center">Không có dữ liệu học sinh</th>';
//        studentScores.innerHTML = '';
//        return;
//    }
//
//    const headers = ['STT', 'Họ và tên', 'Điểm 15 phút', 'Điểm 1 tiết', 'Điểm cuối kỳ'];
//    subjectHeaders.innerHTML = headers.map(header => `<th>${header}</th>`).join('');
//
//    studentScores.innerHTML = students.map((student, index) => `
//        <tr>
//            <td>${index + 1}</td>
//            <td>${student.ho_ten || 'N/A'}</td>
//
//            <td><input type="number" min="0" max="10" step="0.1" class="form-control score-input" data-type="DIEMTX"></td>
//            <td><input type="number" min="0" max="10" step="0.1" class="form-control score-input" data-type="DIEMGK"></td>
//            <td><input type="number" min="0" max="10" step="0.1" class="form-control score-input" data-type="DIEMCK"></td>
//        </tr>
//    `).join('');
//}


//function renderStudentTable(data) {
//    const { students, subjects } = data;
//
//    if (!students || students.length === 0) {
//        subjectHeaders.innerHTML = '<th colspan="8" class="text-center">Không có dữ liệu học sinh</th>';
//        studentScores.innerHTML = '';
//        return;
//    }
//
//    // Headers
//    subjectHeaders.innerHTML = `
//        <th>STT</th>
//        <th>Họ và tên</th>
//        ${subjects.map(subject => `<th>${subject.ten_mon_hoc}</th>`).join('')}
//    `;
//
//    // Students
//    studentScores.innerHTML = students.map((student, index) => `
//        <tr>
//            <td>${index + 1}</td>
//            <td>${student.ho_ten || 'N/A'}</td>
//            ${subjects.map(subject => `
//                <td>
//                    <input type="number" min="0" max="10" step="0.1" class="form-control score-input" data-student-id="${student.id}" data-subject-id="${subject.id}">
//                </td>
//            `).join('')}
//        </tr>
//    `).join('');
//}
// Xóa bảng khi thay đổi lựa chọn
function clearTable() {
    subjectHeaders.innerHTML = '';
    studentScores.innerHTML = '';
}

// Lưu điểm học sinh
saveButton.addEventListener('click', async () => {
    const scores = [];
    const rows = studentScores.getElementsByTagName('tr');

    for (let row of rows) {
        const inputs = row.getElementsByClassName('score-input');
        for (let input of inputs) {
            if (input.value) {
                scores.push({
                    student_id: input.dataset.id,
                    score_type: input.dataset.type,
                    diem: parseFloat(input.value)
                });
            }
        }
    }

    try {
        const response = await fetch('/api/save_scores', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scores, hoc_ky: hocKySelect.value })
        });
        const result = await response.json();

        if (result.message) {
            alert(result.message);
        } else {
            alert('Có lỗi xảy ra khi lưu điểm!');
        }
    } catch (error) {
        console.error('Error saving scores:', error);
        alert('Có lỗi xảy ra khi lưu điểm!');
    }
});

// Khởi tạo trang
fetchNamHoc();


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
//js xử lý xuất bảng điểm



