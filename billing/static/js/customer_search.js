const customerSearchField = document.getElementById("customer_search");
const customerSearchDropdownContainer = document.getElementById("customerSearchDropdownContainer");
const customerID = document.getElementById("customer_id");
const customerName = document.getElementById("customer_name");
const customerPhone = document.getElementById("customer_phone");
const customerState = document.getElementById("customer_state");
const customerAccBal = document.getElementById("customer_account_balance");

document.addEventListener("DOMContentLoaded", () => {
	// getting query
	customerSearchField.addEventListener("focus", () => {
		customerSearchField.value.length > 0 ? null : get_xhr_datas((query = ""));
	});

	customerSearchField.addEventListener("blur", () => {
		setTimeout(() => {
			customerSearchDropdownContainer.style.display = "none";
		}, 500);
	});

	customerSearchField.addEventListener("input", () => {
		get_xhr_datas(customerSearchField.value.trim());
	});

	// getting datas by XHR
	function get_xhr_datas(query) {
		fetch(`/customer_search/?query=${encodeURIComponent(query)}`, {
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
				customers = datas;
				createDropDown(customers);
				// console.log(customers);
			})
			.catch((e) => console.error("Error fetching data"));
	}

	function createDropDown(customers) {
		customerSearchDropdownContainer.innerHTML = ""; // Clear previous dropdown content

		if (customers.length > 0) {
			const dropdown = document.createElement("ul");
			dropdown.className = "dropdown-list";

			customers.forEach((customer) => {
				const item = document.createElement("li");
				item.className = "dropdown-item";
				item.textContent = `${customer.customer_name} - ${customer.customer_id}`;
				item.addEventListener("click", () => {
					///////////////////////////
					customerSearchField.value = "";
					customerID.value = customer.customer_id;
					customerName.value = customer.customer_name;
					customerPhone.value = customer.customer_phone;
					customerState.value = customer.customer_state;
					customerAccBal.value = customer.customer_account_balance;

					clearDropDown();
				});
				dropdown.appendChild(item);
			});

			customerSearchDropdownContainer.appendChild(dropdown);
			customerSearchDropdownContainer.style.display = "block";
		} else {
			customerSearchDropdownContainer.style.display = "none"; // Hide if no results
		}
	}

	function clearDropDown() {
		customerSearchDropdownContainer.innerHTML = "";
		customerSearchDropdownContainer.style.display = "none";
	}
});
