from django import forms
from .models import *

class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductModel
        fields = "__all__"  
        widgets = {
            "product_name": forms.TextInput(attrs={"class": "p-3", "placeholder":"Please type product name"}),
            "product_code": forms.TextInput(attrs={"class": "p-3", "placeholder":"Please type unique product code"}),
            "product_description": forms.TextInput(attrs={"class": "p-3"}),
            "product_hsn": forms.TextInput(attrs={"class": "p-3"}),
            "pack_size": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter pack size (e.g., 10.250)"}),
            "product_packtype": forms.Select(attrs={"class": "form-select"}),
            "product_brand": forms.Select(attrs={"class": "form-select"}),
            "product_category": forms.Select(attrs={"class": "form-select"}),
            "product_barcode": forms.TextInput(attrs={"class": "form-select"}),
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = CustomerModel
        fields = "__all__"
        widgets = {
            "customer_name": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter customer name"
            }),
            "customer_id": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter unique customer id"
            }),
            "customer_email": forms.EmailInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter email address"
            }),
            "customer_phone": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter phone number"
            }),
            "customer_address": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter address"
            }),
            "customer_city": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter city"
            }),
            "customer_state": forms.Select(attrs={
                "class": "form-select"
            }),
            "customer_gst_or_uid": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter GST or UID"
            }),
            "customer_pan": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter PAN number"
            }),
            "customer_account_balance": forms.NumberInput(attrs={
                "class": "form-control", 
                "value": 0
            }),
            "customer_description": forms.Textarea(attrs={
                "class": "form-control", 
                "placeholder": "Enter a brief description", 
                "rows": 3
            }),
            "profile_img": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = SupplierModel
        fields = "__all__"
        widgets = {
            "supplier_name": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter supplier name"
            }),
            "supplier_sub_name": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter sub supplier name"
            }),
            "supplier_id": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter unique supplier id"
            }),
            "supplier_email": forms.EmailInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter email address"
            }),
            "supplier_phone": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter phone number"
            }),
            "supplier_address": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter address"
            }),
            "supplier_city": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter city"
            }),
            "supplier_state": forms.Select(attrs={
                "class": "form-select"
            }),
            "supplier_gst_or_uid": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter GST or UID"
            }),
            "supplier_pan": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter PAN number"
            }),
            "supplier_account_balance": forms.NumberInput(attrs={
                "class": "form-control", 
                "value": 0
            }),
            "supplier_description": forms.Textarea(attrs={
                "class": "form-control", 
                "placeholder": "Enter a brief description", 
                "rows": 3
            }),
            "profile_img": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
        }

class PurchasedStockEntryForm(forms.ModelForm):
    class Meta:
        model = PurchaseStockModel
        # fields = "__all__"
        exclude = ["purchase_bill_id"]
        widgets = {
             "invoice_no": forms.TextInput(attrs={
                "class": "form-control p-3",
                "placeholder": "Enter invoice number"
            }),
              "invoice_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "reference_no_1": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter reference number 1"
            }),
            "reference_no_2": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter reference number 2"
            }),
            "purchase_type": forms.Select(attrs={
                "class": "form-select"
            }),
            "tax_type": forms.CheckboxInput(attrs={
                "class": "form-check-input",
                "style": "width: 50px"
            }),
            "remarks": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter remarks",
                "rows": 3
            }),
            
            # "purchase_bill_id": forms.NumberInput(attrs={
            #     "class": "form-control",
            #     "placeholder": "Enter unique purchase bill ID"
            # }),
            "bill_discount_percentage": forms.NumberInput(attrs={
                "class": "form-control",
                "id" : "bill_discount_percentage"
            }),
            "bill_discount_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "id" : "bill_discount_amount",
                "readonly" : ""
            }),
            "total_discount_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "id" : "total_discount_amount",
                "readonly" : ""
            }),
            "total_tax_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "id" : "total_tax_amount",
                "readonly" : ""
            }),
            "total_units": forms.NumberInput(attrs={
                "class": "form-control",
                "id" : "total_units",
                "readonly" : ""
            }),
            "total_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "id" : "total_amount",
                "readonly" : ""
            }),
            
            # "supplier": forms.Select(attrs={
            #     "class": "form-select"
            # }),
        }

class BillEntryForm(forms.ModelForm):
    class Meta:
        model = BillModel
        # fields = "__all__" 
        exclude = ["bill_id"]
        widgets = {
            "tax_type": forms.CheckboxInput(attrs={
                "class": "form-check-input",
                "style": "width: 50px"
            }),
            # "bill_id": forms.NumberInput(attrs={
            #     "class": "form-control",
            #     "placeholder": "Enter Bill ID"
            # }),
            "bill_discount_percentage": forms.NumberInput(attrs={
                "class": "form-control",
                "id" : "bill_discount_percentage"
            }),
            "bill_discount_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "id" : "bill_discount_amount"
            }),
            "total_discount_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "id" : "total_discount_amount"
            }),
            "total_tax_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "id" : "total_tax_amount"
            }),
            "total_units": forms.NumberInput(attrs={
                "class": "form-control",
                "id" : "total_units"
            }),
            "total_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "id" : "total_amount"
            }),
            "total_paid": forms.NumberInput(attrs={
                "class": "form-control",
                "id" : "total_paid"
            }),
            "balance": forms.NumberInput(attrs={
                "class": "form-control",
                "id" : "balance"
            }),
            # "customer": forms.Select(attrs={
            #     "class": "form-select"
            # }),
            "invoice_no": forms.TextInput(attrs={
                "class": "form-control p-3",
                "placeholder": "Enter Invoice Number"
            }),
            "invoice_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "reference_no_1": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Reference Number 1"
            }),
            "reference_no_2": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Reference Number 2"
            }),
            "purchase_type": forms.Select(attrs={
                "class": "form-select"
            }),
            "remarks": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter any remarks",
                "rows": 3
            }),
        }
