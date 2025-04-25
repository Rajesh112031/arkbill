table = `<table class="table" id="table_head">
            <input type="hidden" id="indexValue" name="indexValue">
            <thead>
                <tr>
                    <th class="product_name">Product</th>
                    <th>Pack Size</th>
                    <th>HSN/Batch</th>
                    <th>Price</th>
                    <th>Quantity</th>
                    <th>Mfg. Date</th>
                    <th>Discount</th>
                    <th>Added Discount</th>
                    <th>SGST</th>
                    <th>CGST</th>
                    <th>IGST</th>
                    <th>Total Quantity</th>
                    <th>Total Tax</th>
                    <th>Total Discount</th>
                    <th>Total Price</th>
                    <th>Grand Total</th>
                </tr>
            </thead>
            <tbody id="table_body">
            </tbody>
        </table>`

tableBody = `<tr>
                <td rowspan="2">
                    Yummy dog food 100kg pack
                </td>
                <td rowspan="">HSN</td>
                <td rowspan="">MRP</td>
                <td rowspan="">QNT</td>
                <td rowspan="">MFG</td>
                <td>%</td>
                <td>%</td>
                <td>%</td>
                <td>%</td>
                <td>%</td>
                <td rowspan="2">QNt</td>
                <td rowspan="2">Tax AMt.</td>
                <td rowspan="2">Discount</td>
                <td rowspan="2">Total</td>
            </tr>
            <tr>
                <td>BATCH</td>
                <td>Sales Prize</td>
                <td>Free QNT</td>
                <td>EXP</td>
                <td>Amt</td>
                <td>Amt</td>
                <td>Amt</td>
                <td>Amt</td>
                <td>Amt</td>
            </tr>
`

var index = 1;
var overAllTotalTax = 0; 
var overAllTotalPrice = 0;  
var overAllTotalDiscount = 0; 
var overAllTotal = 0; 
var overAllUnits = 0;
var bill_discount_amount = 0;

function addStock(){
    if (document.getElementById("product_name").value.trim() == "" || document.getElementById("sales_price").value.trim() == "" || document.getElementById("quantity").value.trim() == ""){
        return;
    }
    if (!document.getElementById("table_head")){
        document.getElementById("table_purchase").innerHTML = table;
    }
    let tableRow = `
    <tr>
        <td rowspan="2">
            ${document.getElementById("product_name").value}
            <input type="hidden" value="${document.getElementById("product_name").value}" name="product_name_${index}" hidden>
            
            <input type="hidden" value="${document.getElementById("product_id").value}" name="product_id_${index}" hidden>
            
        </td>
        <td rowspan="2">
            ${document.getElementById("pack_size").value}
            <input type="hidden" value="${document.getElementById("pack_size").value}" name="pack_size_${index}" hidden>
        </td>
        <td rowspan="">
            ${document.getElementById("hsn").value}
            <input type="hidden" value="${document.getElementById("hsn").value}" name="hsn_${index}" hidden>
        </td>
        <td rowspan="">
            ${document.getElementById("mrp").value}
            <input type="hidden" value="${document.getElementById("mrp").value}" name="mrp_${index}" hidden>
        </td>
        <td rowspan="">
            ${document.getElementById("quantity").value}
            <input type="hidden" value="${document.getElementById("quantity").value}" name="quantity_${index}" hidden>
        </td>
        <td rowspan="">
            ${document.getElementById("manufacture").value}
            <input type="hidden" value="${document.getElementById("manufacture").value}" name="manufacture_${index}" hidden>
        </td>
        <td>
            ${document.getElementById("discount_percentage").value}
            <input type="hidden" value="${document.getElementById("discount_percentage").value}" name="discount_percentage_${index}" hidden>
        </td>
        <td>
            ${document.getElementById("added_discount").value}
            <input type="hidden" value="${document.getElementById("added_discount").value}" name="added_discount_${index}" hidden>
        </td>
        <td>
            ${document.getElementById("sgst").value}
            <input type="hidden" value="${document.getElementById("sgst").value}" name="sgst_${index}" hidden>
        </td>
        <td>
            ${document.getElementById("cgst").value}
            <input type="hidden" value="${document.getElementById("cgst").value}" name="cgst_${index}" hidden>
        </td>
        <td>
            ${document.getElementById("igst").value}
            <input type="hidden" value="${document.getElementById("igst").value}" name="igst_${index}" hidden>
        </td>
        <td rowspan="2">
            ${document.getElementById("total_quantity").value}
            <input type="hidden" value="${document.getElementById("total_quantity").value}" name="total_quantity_${index}" hidden>
        </td>
        <td rowspan="2">
            ${document.getElementById("totalTax").value}
            <input type="hidden" value="${document.getElementById("totalTax").value}" name="totalTax_${index}" hidden>
        </td>
        <td rowspan="2">
            ${parseInt(document.getElementById("discount_amount").value) + parseInt(document.getElementById("added_discount_amount").value)}
            <input type="hidden" value="${parseInt(document.getElementById("discount_amount").value) + parseInt(document.getElementById("added_discount_amount").value)}" name="totalDiscount_${index}" hidden>
        </td>
        <td rowspan="2">
            ${document.getElementById("total_price").value}
            <input type="hidden" value="${document.getElementById("total_price").value}" name="total_price_${index}" hidden>
        </td>
        <td rowspan="2">
            ${document.getElementById("grandTotal").value}
            <input type="hidden" value="${document.getElementById("grandTotal").value}" name="grandTotal_${index}" hidden>
        </td>
    </tr>
    <tr>
        <td>
            ${document.getElementById("batch").value}
            <input type="hidden" value="${document.getElementById("batch").value}" name="batch_${index}" hidden>
        </td>
        <td>
            ${document.getElementById("sales_price").value}
            <input type="hidden" value="${document.getElementById("sales_price").value}" name="sales_price_${index}" hidden>
        </td>
        <td>
            ${document.getElementById("free_quantity").value}
            <input type="hidden" value="${document.getElementById("free_quantity").value}" name="free_quantity_${index}" hidden>
        </td>
        <td>
            ${document.getElementById("expiring").value}
            <input type="hidden" value="${document.getElementById("expiring").value}" name="expiring_${index}" hidden>
        </td>
        <td>
            ${document.getElementById("discount_amount").value}
            <input type="hidden" value="${document.getElementById("discount_amount").value}" name="discount_amount_${index}" hidden>
        </td>
        <td>
            ${document.getElementById("added_discount_amount").value}
            <input type="hidden" value="${document.getElementById("added_discount_amount").value}" name="added_discount_amount_${index}" hidden>
        </td>
        <td>
            ${document.getElementById("sgst_amount").value}
            <input type="hidden" value="${document.getElementById("sgst_amount").value}" name="sgst_amount_${index}" hidden>
        </td>
        <td>
            ${document.getElementById("cgst_amount").value}
            <input type="hidden" value="${document.getElementById("cgst_amount").value}" name="cgst_amount_${index}" hidden>
        </td>
        <td>
            ${document.getElementById("igst_amount").value}
            <input type="hidden" value="${document.getElementById("igst_amount").value}" name="igst_amount_${index}" hidden>
        </td>
    </tr>
    `
    document.getElementById("table_body").innerHTML += tableRow;
    document.getElementById("indexValue").value = index;

    overAllTotalTax += parseInt(document.getElementById("totalTax").value);
    overAllTotalDiscount += parseInt(document.getElementById("discount_amount").value) + parseInt(document.getElementById("added_discount_amount").value);
    overAllTotalPrice += parseInt(document.getElementById("total_price").value);
    overAllTotal += parseInt(document.getElementById("grandTotal").value);
    overAllUnits += parseInt(document.getElementById("total_quantity").value);

	document.getElementById("overAllTotalTax").innerHTML = overAllTotalTax;
	document.getElementById("overAllTotalDiscount").innerHTML = overAllTotalDiscount;
	document.getElementById("overAllTotalPrice").innerHTML = overAllTotalPrice;
	document.getElementById("overAllTotal").innerHTML = overAllTotal;
    
	document.getElementById("total_tax_amount").value = overAllTotalTax;
    document.getElementById("total_units").value = overAllUnits;
	
    lastDatas();
    emptyFields();

    index += 1;
}

const bill_discount_percentage = document.getElementById("bill_discount_percentage");

bill_discount_percentage.addEventListener("input", () => {
    bill_discount_amount = Math.round((bill_discount_percentage.value * overAllTotal) / 100);
    document.getElementById("bill_discount_amount").value = bill_discount_amount;
    lastDatas();
})

function lastDatas(){
    document.getElementById("total_discount_amount").value = overAllTotalDiscount + bill_discount_amount;
	document.getElementById("total_amount").value = overAllTotal - bill_discount_amount;
}