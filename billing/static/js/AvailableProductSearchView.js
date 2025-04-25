const productSearchField = document.getElementById("product_search");
const productSearchDropdownContainer = document.getElementById("productSearchDropdownContainer");
const product_id = document.getElementById("product_id");
const product_name = document.getElementById("product_name");
const product_code = document.getElementById("product_code");
const product_hsn = document.getElementById("hsn");
const product_packtype = document.getElementById("product_packtype");
const product_barcode = document.getElementById("product_barcode");
const pack_size = document.getElementById("pack_size");
const batch = document.getElementById("batch");
const mrp_in = document.getElementById("mrp");
const sales_price_in = document.getElementById("sales_price");
const stock_available_in = document.getElementById("stock_available");
const manufacture = document.getElementById("manufacture");
const expiring = document.getElementById("expiring");

document.addEventListener("DOMContentLoaded", () => {
	// getting query
	productSearchField.addEventListener("focus", () => {
		productSearchField.value.length > 0 ? null : get_xhr_datas((query = ""));
	});

	productSearchField.addEventListener("blur", () => {
		setTimeout(() => {
			productSearchDropdownContainer.style.display = "none";
		}, 500);
	});

	productSearchField.addEventListener("input", () => {
		get_xhr_datas(productSearchField.value.trim());
	});

	// getting datas by XHR
	function get_xhr_datas(query) {
		fetch(`/product_available_search/?query=${encodeURIComponent(query)}`, {
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
				// console.log(products);
			})
			.catch((e) => console.error("Error fetching data"));
	}

	function createProductDropDown(products) {
		productSearchDropdownContainer.innerHTML = "";

		if (products.length > 0) {
			const dropdownproduct = document.createElement("ul");
			dropdownproduct.className = "dropdown-list";

			products.forEach((product) => {
				const itemproduct = document.createElement("li");
				itemproduct.className = "dropdown-item";
				itemproduct.textContent = `${product.product__product_name} - ${product.product__product_code}`;
				itemproduct.addEventListener("click", () => {
					///////////////////////////
					productSearchField.value = "";
					product_id.value = product.id;
					product_name.value = product.product__product_name;
					product_code.value = product.product__product_code;
					product_hsn.value = product.product__product_hsn;
					product_packtype.value = product.product__product_packtype;
					batch.value = product.batch_no;
					mrp_in.value = product.mrp;
					sales_price_in.value = product.sales_price;
					product_barcode.value = product.product__product_barcode;
					stock_available_in.value = product.units;
					manufacture.value = formatDate(product.manufacturing);
					expiring.value = formatDate(product.expiring);

					

					clearDropDownProduct();
				});
				dropdownproduct.appendChild(itemproduct);
			});

			productSearchDropdownContainer.appendChild(dropdownproduct);
			productSearchDropdownContainer.style.display = "block";
		} else {
			productSearchDropdownContainer.style.display = "none";
		}
	}

	function clearDropDownProduct() {
		productSearchDropdownContainer.innerHTML = "";
		productSearchDropdownContainer.style.display = "none";
	}
});
function formatDate(dateStr) {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    return date.toISOString().slice(0, 10); // Format to yyyy-MM-dd
}