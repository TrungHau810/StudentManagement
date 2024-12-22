function loadHocsinh() {
    let nam_hoc = document.getElementById("namHoc").value;
    let ten_lop = document.getElementById("lop").value;
    let tableBody = document.getElementById("hocsinh_body");
    tableBody.innerHTML = "";
    fetch('/api/get_hocsinh', {
        method: "POST", body: JSON.stringify({
            nam_hoc: nam_hoc,
            ten_lop: ten_lop
        }), headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(data => {
        data.hs.forEach(h => {
            let tableBody = document.getElementById("hocsinh_body");
            tableBody.innerHTML = "";
            let soThuTu = 0;

            let dropdown = `<select class="dropdown-lop">`;
            data.lop.forEach(l => {
                dropdown += `<option value="${l.id}" ${l.ten_lop === h.ten_lop ? 'selected' : ''}>${l.ten_lop}</option>`;
            });
            dropdown += `</select>`;

            soThuTu++;

            // let row = document.createElement("tr");
            tableBody.innerHTML = `
                <tr class="${h.id}">
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