const productSearchField = document.getElementById("product_search");
const productSearchDropdownContainer = document.getElementById('productSearchDropdownContainer');
const product_id = document.getElementById("product_id");
const product_name = document.getElementById("product_name");
const product_code = document.getElementById("product_code");
const product_hsn = document.getElementById("hsn");
const product_barcode = document.getElementById("product_barcode");
const product_packtype = document.getElementById("product_packtype");
const pack_size = document.getElementById("pack_size");


document.addEventListener("DOMContentLoaded", () => {
	// getting query
	productSearchField.addEventListener("focus", () => {
		productSearchField.value.length > 0 ? null : get_xhr_datas((query = ""));
	});
	
    productSearchField.addEventListener("blur", () => {
        setTimeout(() => {
            productSearchDropdownContainer.style.display = 'none';
        }, 500);
    });
    

    productSearchField.addEventListener("input", () => {
		get_xhr_datas(productSearchField.value.trim());
	});

    // getting datas by XHR
	function get_xhr_datas(query) {
		fetch(`/product_search/?query=${encodeURIComponent(query)}`, {
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
				createProductDropDown(products);
                console.log(products);
			})
			.catch((e) => console.error("Error fetching data"));
	}

    function createProductDropDown(products) {
        productSearchDropdownContainer.innerHTML = '';
        if (products.length > 0) {
            const dropdownproduct = document.createElement('ul');
            dropdownproduct.className = 'dropdown-list';
    
            products.forEach(product => {
                const itemproduct = document.createElement('li');
                itemproduct.className = 'dropdown-item';
                itemproduct.textContent = `${product.product_name} - ${product.product_code}`;
                itemproduct.addEventListener('click', () => {
                    ///////////////////////////
                    productSearchField.value = "";
                    product_name.value = product.product_name;
                    product_code.value = product.product_code;
                    product_hsn.value = product.product_hsn;
                    product_barcode.value = product.product_barcode;
                    product_packtype.value = `${product.pack_size} ${product.product_packtype}`;
                    pack_size.value = product.pack_size;
                    product_id.value = product.id;
                    
                    clearDropDownProduct();
                });
                dropdownproduct.appendChild(itemproduct);
            });
    
            productSearchDropdownContainer.appendChild(dropdownproduct);
            productSearchDropdownContainer.style.display = 'block';
        } else {
            productSearchDropdownContainer.style.display = 'none';
        }
    }

    function clearDropDownProduct() {
        productSearchDropdownContainer.innerHTML = '';
        productSearchDropdownContainer.style.display = 'none';
    }

});
