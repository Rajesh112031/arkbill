function calculateTotalPrize() {
	// Get field values
	const mrp = parseInt(document.getElementById("mrp").value) || 0;
	const salesPrice = parseInt(document.getElementById("sales_price").value) || 0;
	const quantity = parseInt(document.getElementById("quantity").value) || 0;
	const freeQuantity = parseInt(document.getElementById("free_quantity").value) || 0;
	const discountPercentage = parseInt(document.getElementById("discount_percentage").value) || 0;
	const addedDiscountPercentage = parseInt(document.getElementById("added_discount").value) || 0;
	const sgstPercentage = parseInt(document.getElementById("sgst").value) || 0;
	const cgstPercentage = parseInt(document.getElementById("cgst").value) || 0;
	const igstPercentage = parseInt(document.getElementById("igst").value) || 0;

	// Calculate discounts
	const totalDiscountAmount = Math.round(((salesPrice * discountPercentage) / 100));
	const addedDiscountAmount = Math.round(((salesPrice * addedDiscountPercentage) / 100));

	// Calculate tax
	const taxableAmount = Math.round((salesPrice - totalDiscountAmount - addedDiscountAmount));
	const sgstAmount = Math.round(((taxableAmount * sgstPercentage) / 100));
	const cgstAmount = Math.round(((taxableAmount * cgstPercentage) / 100));
	const igstAmount = Math.round(((taxableAmount * igstPercentage) / 100));

	// Calculate totals
	const totalTax =Math.round(parseInt(sgstAmount) + parseInt(cgstAmount) + parseInt(igstAmount));
	const grandTotal = Math.round((taxableAmount * quantity + totalTax));
	const totalQuantity = quantity + freeQuantity;

	// Update the DOM
	document.getElementById("discount_amount").value = Math.round(totalDiscountAmount);
	document.getElementById("added_discount_amount").value = Math.round(addedDiscountAmount);
	document.getElementById("sgst_amount").value = Math.round(sgstAmount);
	document.getElementById("cgst_amount").value = Math.round(cgstAmount);
	document.getElementById("igst_amount").value = Math.round(igstAmount);
	document.getElementById("total_quantity").value = Math.round(totalQuantity);
	document.getElementById("totalTax").value = Math.round(totalTax);
	
	document.getElementById("total_price").value = Math.round((taxableAmount * quantity));
	document.getElementById("grandTotal").value = Math.round(grandTotal);

}

function emptyFields() {
    const fieldsToClear = [
        "product_name",
        "sales_price",
        "quantity",
        "free_quantity",
        "mrp",
        "discount_percentage",
        "added_discount",
        "sgst",
        "cgst",
        "igst",
        "manufacture",
        "batch",
        "expiring",
        "totalTax",
        "discount_amount",
        "added_discount_amount",
        "sgst_amount",
        "cgst_amount",
        "igst_amount",
        "total_quantity",
        "total_price",
        "grandTotal"
    ];

    fieldsToClear.forEach(fieldId => {
		if (document.getElementById(fieldId)){
			document.getElementById(fieldId).value = "";
		}
    });
}
