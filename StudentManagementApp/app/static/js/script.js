function addLopToDropdown(khoi){
    fetch('/api/get_lop_by_khoi',{
        method: "POST",
        body: JSON.stringify({khoi: khoi}),
        headers:{
            'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(data => {

    })
}