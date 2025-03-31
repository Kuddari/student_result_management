document.addEventListener("DOMContentLoaded", function () {
    const provinceField = document.getElementById("id_province");
    const districtField = document.getElementById("id_district");
    const subdistrictField = document.getElementById("id_subdistrict");
    const postalCodeField = document.getElementById("id_postal_code");

    function clearOptions(field) {
        field.innerHTML = '<option value="">---------</option>';
    }

    function fetchOptions(url, field) {
        fetch(url)
            .then(response => response.json())
            .then(data => {
                clearOptions(field);
                data.forEach(item => {
                    const option = document.createElement("option");
                    option.value = item.id;
                    option.textContent = item.name;
                    field.appendChild(option);
                });
            });
    }

    provinceField.addEventListener("change", function () {
        const provinceId = this.value;
        clearOptions(districtField);
        clearOptions(subdistrictField);
        postalCodeField.value = "";

        if (provinceId) {
            fetch(`/admin/get-districts/?province_id=${provinceId}`)
                .then(response => response.json())
                .then(data => {
                    data.forEach(item => {
                        const option = document.createElement("option");
                        option.value = item.id;
                        option.textContent = item.name;
                        districtField.appendChild(option);
                    });
                });
        }
    });

    districtField.addEventListener("change", function () {
        const districtId = this.value;
        clearOptions(subdistrictField);
        postalCodeField.value = "";

        if (districtId) {
            fetch(`/admin/get-subdistricts/?district_id=${districtId}`)
                .then(response => response.json())
                .then(data => {
                    data.forEach(item => {
                        const option = document.createElement("option");
                        option.value = item.id;
                        option.textContent = item.name;
                        subdistrictField.appendChild(option);
                    });
                });
        }
    });

    subdistrictField.addEventListener("change", function () {
        const subdistrictId = this.value;
        if (subdistrictId) {
            fetch(`/admin/get-postal-code/?subdistrict_id=${subdistrictId}`)
                .then(response => response.json())
                .then(data => {
                    postalCodeField.value = data.zipcode;
                });
        }
    });
});
