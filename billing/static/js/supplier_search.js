const supplierSearchField = document.getElementById("supplier_search")
const supplierSearchDropdownContainer = document.getElementById('supplierSearchDropdownContainer');
const supplierID = document.getElementById("supplier_id")
const supplierName = document.getElementById("supplier_name")
const supplierPhone = document.getElementById("supplier_phone")
const supplierState = document.getElementById("supplier_state")
const supplierAccBal = document.getElementById("supplier_account_balance")


document.addEventListener("DOMContentLoaded", () => {
	// getting query
	supplierSearchField.addEventListener("focus", () => {
		supplierSearchField.value.length > 0 ? null : get_xhr_datas((query = ""));
	});
	
    supplierSearchField.addEventListener("blur", () => {
        setTimeout(() => {
            supplierSearchDropdownContainer.style.display = 'none';
        }, 500);
    });
    

    supplierSearchField.addEventListener("input", () => {
		get_xhr_datas(supplierSearchField.value.trim());
	});

    // getting datas by XHR
	function get_xhr_datas(query) {
		fetch(`/supplier_search/?query=${encodeURIComponent(query)}`, {
			headers: {
				"X-Requested-With": "XMLHttpRequest",
			},
		})
			.then((response) => {
				if (!response.ok) {
                    // console.error(response);
					throw new Error("error");
				}
				return response.json();
			})
			.then((datas) => {
				products = datas;
				createDropDown(products);
                // console.log(products);
			})
			.catch((e) => console.error("Error fetching data"));
	}

    function createDropDown(products) {
        supplierSearchDropdownContainer.innerHTML = '';
    
        if (products.length > 0) {
            const dropdown = document.createElement('ul');
            dropdown.className = 'dropdown-list';
    
            products.forEach(supplier => {
                const item = document.createElement('li');
                item.className = 'dropdown-item';
                item.textContent = `${supplier.supplier_name} - ${supplier.supplier_id}`;
                item.addEventListener('click', () => {
                    ///////////////////////////
                    supplierSearchField.value = "";
                    supplierID.value = supplier.supplier_id;
                    supplierName.value = supplier.supplier_name;
                    supplierPhone.value = supplier.supplier_phone;
                    supplierState.value = supplier.supplier_state;
                    supplierAccBal.value = supplier.supplier_account_balance;
                    
                    clearDropDown();
                });
                dropdown.appendChild(item);
            });
    
            supplierSearchDropdownContainer.appendChild(dropdown);
            supplierSearchDropdownContainer.style.display = 'block';
        } else {
            supplierSearchDropdownContainer.style.display = 'none'; 
        }
    }

    function clearDropDown() {
        supplierSearchDropdownContainer.innerHTML = '';
        supplierSearchDropdownContainer.style.display = 'none';
    }

});
