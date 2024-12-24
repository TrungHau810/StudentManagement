// Khởi tạo các elements
const namHocSelect = document.getElementById('namHoc');
const hocKySelect = document.getElementById('hocKy');
const lopSelect = document.getElementById('lop');
const monHocSelect = document.getElementById('monHoc');
const studentScores = document.getElementById('studentScores');

// Fetch năm học khi trang load
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
namHocSelect.addEventListener('change', function() {
    const namHoc = this.value;
    if (!namHoc) {
        hocKySelect.disabled = true;
        lopSelect.disabled = true;
        monHocSelect.disabled = true;
        clearTable();
        return;
    }

    // Reset và enable học kỳ
    hocKySelect.innerHTML = `
        <option value="">-- Chọn học kỳ --</option>
        <option value="HK1">Học kỳ 1</option>
        <option value="HK2">Học kỳ 2</option>
    `;
    hocKySelect.disabled = false;

    // Reset và disable các select khác
    lopSelect.innerHTML = '<option value="">-- Chọn lớp --</option>';
    monHocSelect.innerHTML = '<option value="">-- Chọn môn học --</option>';
    lopSelect.disabled = true;
    monHocSelect.disabled = true;

    clearTable();
});

// Khi chọn học kỳ
hocKySelect.addEventListener('change', async function() {
    const hocKy = this.value;
    const namHoc = namHocSelect.value;

    if (!hocKy || !namHoc) {
        lopSelect.disabled = true;
        monHocSelect.disabled = true;
        clearTable();
        return;
    }

    try {
        console.log('Fetching lớp with:', { namHoc, hocKy });

        const response = await fetch('/api/get_lop_by_namhoc_hocky', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                nam_hoc: namHoc,
                hoc_ky: hocKy
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Received data:', data);

        // Reset lớp select
        lopSelect.innerHTML = '<option value="">-- Chọn lớp --</option>';

        // Kiểm tra xem data có phải là array không
        if (Array.isArray(data.lop)) {
            data.lop.forEach(lop => {
                lopSelect.innerHTML += `<option value="${lop.id}">${lop.ten}</option>`;
            });
        } else {
            console.error('Data is not in expected format:', data);
            throw new Error('Invalid data format received from server');
        }

        // Enable lớp select
        lopSelect.disabled = false;

        // Disable và reset môn học select
        monHocSelect.innerHTML = '<option value="">-- Chọn môn học --</option>';
        monHocSelect.disabled = true;

        clearTable();
    } catch (error) {
        console.error('Error fetching lớp:', error);
        alert('Có lỗi khi tải danh sách lớp: ' + error.message);

        // Reset và disable các select phía sau
        lopSelect.innerHTML = '<option value="">-- Chọn lớp --</option>';
        lopSelect.disabled = true;
        monHocSelect.innerHTML = '<option value="">-- Chọn môn học --</option>';
        monHocSelect.disabled = true;

        clearTable();
    }
});
// Khi chọn lớp
lopSelect.addEventListener('change', async function() {
    const lopId = this.value;
    const hocKy = hocKySelect.value;
    const namHoc = namHocSelect.value;

    if (!lopId || !hocKy || !namHoc) {
        monHocSelect.disabled = true;
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

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Lỗi server');
        }

        console.log('Received môn học data:', data);

        // Reset môn học select
        monHocSelect.innerHTML = '<option value="">-- Chọn môn học --</option>';

        if (data.mon_hoc && Array.isArray(data.mon_hoc)) {
            data.mon_hoc.forEach(mon => {
                monHocSelect.innerHTML += `<option value="${mon.id}">${mon.ten_mon_hoc}</option>`;
            });
            monHocSelect.disabled = false;
        } else {
            throw new Error('Không có dữ liệu môn học');
        }

        clearTable();
    } catch (error) {
        console.error('Error fetching môn học:', error);
        alert('Có lỗi khi tải danh sách môn học: ' + error.message);

        monHocSelect.innerHTML = '<option value="">-- Chọn môn học --</option>';
        monHocSelect.disabled = true;
        clearTable();
    }
});

// Khi chọn môn học
monHocSelect.addEventListener('change', async function() {
    const monHocId = this.value;
    if (!monHocId) {
        clearTable();
        return;
    }

    try {
        const response = await fetch('/api/get_bangdiem', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nam_hoc: namHocSelect.value,
                hoc_ky: hocKySelect.value,
                lop_id: lopSelect.value,
                mon_hoc_id: monHocId
            })
        });

        const data = await response.json();
        if (data && data.length > 0) {
            document.getElementById('classContent').style.display = 'block';
            renderBangDiem(data);
        } else {
            clearTable();
            alert('Không có dữ liệu điểm cho lớp và môn học này');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Có lỗi khi tải bảng điểm');
        clearTable();
    }
});

// Render bảng điểm
function renderBangDiem(students) {
    studentScores.innerHTML = students.map((student, index) => `
        <tr>
            <td>${index + 1}</td>
            <td>${student.ma_hs}</td>
            <td>${student.ho_ten}</td>
            <td>${student.diem_tx || ''}</td>
            <td>${student.diem_gk || ''}</td>
            <td>${student.diem_ck || ''}</td>
        </tr>
    `).join('');
}

function clearTable() {
    studentScores.innerHTML = '';
    document.getElementById('classContent').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing...');
    fetchNamHoc();
});

