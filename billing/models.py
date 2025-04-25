from django.db import models
from django.db.models import Sum

purchase_type_choice = [('cash', 'Cash'),
                        ('card', 'Card'),
                        ('online pay', 'Online Pay')]

states_choice = [
    ('Andhra Pradesh [37]', 'Andhra Pradesh [37]'),
    ('Arunachal Pradesh [12]', 'Arunachal Pradesh [12]'),
    ('Assam [18]', 'Assam [18]'),
    ('Bihar [10]', 'Bihar [10]'),
    ('Chhattisgarh [22]', 'Chhattisgarh [22]'),
    ('Goa [30]', 'Goa [30]'),
    ('Gujarat [24]', 'Gujarat [24]'),
    ('Haryana [06]', 'Haryana [06]'),
    ('Himachal Pradesh [02]', 'Himachal Pradesh [02]'),
    ('Jharkhand [20]', 'Jharkhand [20]'),
    ('Karnataka [29]', 'Karnataka [29]'),
    ('Kerala [32]', 'Kerala [32]'),
    ('Madhya Pradesh [23]', 'Madhya Pradesh [23]'),
    ('Maharashtra [27]', 'Maharashtra [27]'),
    ('Manipur [14]', 'Manipur [14]'),
    ('Meghalaya [17]', 'Meghalaya [17]'),
    ('Mizoram [15]', 'Mizoram [15]'),
    ('Nagaland [13]', 'Nagaland [13]'),
    ('Odisha [21]', 'Odisha [21]'),
    ('Punjab [03]', 'Punjab [03]'),
    ('Rajasthan [08]', 'Rajasthan [08]'),
    ('Sikkim [11]', 'Sikkim [11]'),
    ('Tamil Nadu [33]', 'Tamil Nadu [33]'),
    ('Telangana [36]', 'Telangana [36]'),
    ('Tripura [16]', 'Tripura [16]'),
    ('Uttar Pradesh [09]', 'Uttar Pradesh [09]'),
    ('Uttarakhand [05]', 'Uttarakhand [05]'),
    ('West Bengal [19]', 'West Bengal [19]'),
    ('Andaman and Nicobar Islands [35]', 'Andaman and Nicobar Islands [35]'),
    ('Chandigarh [04]', 'Chandigarh [04]'),
    ('Dadra and Nagar Haveli and Daman and Diu [26]', 'Dadra and Nagar Haveli and Daman and Diu [26]'),
    ('Delhi [07]', 'Delhi [07]'),
    ('Jammu and Kashmir [01]', 'Jammu and Kashmir [01]'),
    ('Ladakh [38]', 'Ladakh [38]'),
    ('Lakshadweep [31]', 'Lakshadweep [31]'),
    ('Puducherry [34]', 'Puducherry [34]'),
]

pack_type_choices = [('kg','Kg'),
                     ('pack','Pack'),
                     ('littre','Littre'),
                     ('bottle','Bottle')]

class ProductBrandModel(models.Model):
    brand = models.CharField(max_length=50)
    brand_description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        if self.brand_description:
            return f"{self.brand} - {self.brand_description[:10]}{'...' if len(self.brand_description) > 10 else ''}"
        return f"{self.brand}"
            
class ProductCategoryModel(models.Model):
    category = models.CharField(max_length=50)
    category_description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        if self.category_description:
            return f"{self.category} - {self.category_description[:10]}{'...' if len(self.category_description) > 10 else ''}"
        return f"{self.category}"

class ProductModel(models.Model):
    product_name = models.CharField(max_length=150)
    product_code = models.CharField(unique=True, max_length=50)
    product_description = models.TextField(null=True, blank=True)
    product_brand = models.ForeignKey(ProductBrandModel, on_delete=models.CASCADE)
    product_category = models.ForeignKey(ProductCategoryModel, on_delete=models.CASCADE)
    product_hsn = models.CharField(max_length=50)
    product_barcode = models.CharField(max_length=50, null=True, blank=True)
    product_packtype = models.CharField(choices=pack_type_choices, max_length=50, default="Kg")
    pack_size = models.DecimalField(max_digits=10, decimal_places=3)
    reorder_unit = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    @property
    def stock_in(self):
        return self.purchasestockproductmodel_set.aggregate(
            total_in=Sum('total_quantity')
        )['total_in'] or 0

    @property
    def stock_out(self):
        return self.billproductmodel_set.aggregate(
            total_out=Sum('units')
        )['total_out'] or 0

    @property
    def get_current_stock(self):
        return self.stock_in - self.stock_out

    class Meta:
        ordering = ["-created_at"]
        
class SupplierModel(models.Model):
    profile_img = models.ImageField(upload_to="supplier", max_length=None, null=True, blank=True)
    supplier_id = models.CharField(max_length=50, unique=True)
    supplier_name = models.CharField(max_length=50)
    supplier_sub_name = models.CharField(max_length=50,null=True, blank=True)
    supplier_email = models.EmailField(max_length=254, null=True, blank=True)
    supplier_phone = models.IntegerField(null=True, blank=True)
    supplier_address = models.TextField(null=True, blank=True)
    supplier_city = models.CharField(max_length=150, null=True, blank=True)
    supplier_state = models.CharField(max_length=150, choices=states_choice)
    supplier_description = models.TextField(null=True, blank=True)
    supplier_gst_or_uid = models.CharField(max_length=50, null=True, blank=True)
    supplier_pan = models.CharField(max_length=50, null=True, blank=True)
    supplier_account_balance = models.IntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"{self.supplier_name} - {self.supplier_id}"

    class Meta:
        ordering = ["-created_at"]

class CustomerModel(models.Model):
    profile_img = models.ImageField(upload_to="customer", max_length=None, null=True, blank=True)
    customer_id = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=50)
    customer_email = models.EmailField(max_length=254, null=True, blank=True)
    customer_phone = models.IntegerField(null=True, blank=True)
    customer_address = models.TextField(null=True, blank=True)
    customer_city = models.CharField(max_length=150, null=True, blank=True)
    customer_state = models.CharField(max_length=150, choices=states_choice)
    customer_description = models.TextField(null=True, blank=True)
    customer_gst_or_uid = models.CharField(max_length=50, null=True, blank=True)
    customer_pan = models.CharField(max_length=50, null=True, blank=True)
    customer_account_balance = models.IntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
    
    def __str__(self):
        return f"{self.customer_name} - {self.customer_id}"
    
    class Meta:
        ordering = ["-created_at"]

class PurchaseStockModel(models.Model):
    tax_type = models.BooleanField(default=False) # True tax inclusive
    purchase_bill_id = models.IntegerField(unique=True)
    bill_discount_percentage = models.IntegerField(null=True, blank=True)
    bill_discount_amount = models.IntegerField(null=True, blank=True)
    total_discount_amount = models.IntegerField(null=True, blank=True)
    total_tax_amount = models.IntegerField(null=True, blank=True)
    total_units = models.IntegerField()
    total_amount = models.IntegerField()
    
    supplier = models.ForeignKey(SupplierModel, on_delete=models.SET_NULL, null=True, blank=True)
    
    invoice_no = models.CharField(max_length=50)
    invoice_date = models.DateField(auto_now=False, auto_now_add=False)
    reference_no_1 = models.CharField(max_length=50, null=True, blank=True)
    reference_no_2 = models.CharField(max_length=50, null=True, blank=True)
    purchase_type = models.CharField(choices=purchase_type_choice, max_length=50, default="cash")
    remarks = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
 
    # def __str__(self):
    #     return f"{self.purchase_bill_id} - {self.supplier.supplier_name}"
    
    class Meta:
        ordering = ["-created_at"]
    
class PurchaseStockProductModel(models.Model):
    purchase_stock = models.ForeignKey(PurchaseStockModel, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel, on_delete=models.SET_NULL, null=True, blank=True)
    hsn = models.CharField(max_length=50)
    pack_size = models.DecimalField(max_digits=5, decimal_places=3)
    mrp = models.IntegerField()
    sales_price = models.IntegerField()
    batch_no = models.CharField(max_length=50)
    discount_percentage_1 = models.IntegerField( null=True, blank=True, default=0) ###################
    discount_amount_1 = models.IntegerField( null=True, blank=True, default=0) ###################
    discount_percentage_2 = models.IntegerField( null=True, blank=True, default=0) ###################
    discount_amount_2 = models.IntegerField( null=True, blank=True, default=0) ###################
    units = models.IntegerField(default=1)
    discount_unit = models.IntegerField( null=True, blank=True, default=0)
    sgst_percentage = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True, default=0)
    sgst_amount = models.IntegerField( null=True, blank=True, default=0)
    cgst_percentage = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True, default=0)
    cgst_amount = models.IntegerField( null=True, blank=True, default=0)
    igst_percentage = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True, default=0)
    igst_amount = models.IntegerField( null=True, blank=True, default=0)
    buy_price = models.IntegerField( null=True, blank=True, default=0)
    
    manufacturing = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    expiring = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    
    total_quantity = models.IntegerField(null=True)
    total_price = models.IntegerField(null=True)
    totalTax = models.IntegerField(null=True, blank=True, default=0)
    grandTotal = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    
    def __str__(self):
        return f"{self.product.product_name} - {self.pack_size} kg/pck - {self.mrp}"
    
    class Meta:
        ordering = ["-created_at"]
    
class BillModel(models.Model):
    tax_type = models.BooleanField(default=False) # True tax inclusive
    bill_id = models.IntegerField(unique=True)
    bill_discount_percentage = models.IntegerField(null=True, blank=True, default=0)
    bill_discount_amount = models.IntegerField(null=True, blank=True, default=0)
    total_discount_amount = models.IntegerField(null=True, blank=True, default=0)
    total_tax_amount = models.IntegerField(null=True, blank=True, default=0)
    total_units = models.IntegerField()
    total_amount = models.IntegerField()
    total_paid = models.IntegerField( null=True, blank=True, default=0)
    balance = models.IntegerField( null=True, blank=True, default=0)
    
    customer = models.ForeignKey(CustomerModel, on_delete=models.SET_NULL, null=True, blank=True)
    
    invoice_no = models.CharField(max_length=50)
    invoice_date = models.DateField(auto_now=False, auto_now_add=False)
    reference_no_1 = models.CharField(max_length=50, null=True, blank=True)
    reference_no_2 = models.CharField(max_length=50, null=True, blank=True)
    purchase_type = models.CharField(choices=purchase_type_choice, max_length=50, default="cash")
    remarks = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    is_estimation = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer} - {self.customer.customer_name}"
    
    class Meta:
        ordering = ["-created_at"]
    
class BillProductModel(models.Model):
    bill = models.ForeignKey(BillModel, on_delete=models.CASCADE)
    product = models.ForeignKey(PurchaseStockProductModel, on_delete=models.SET_NULL, null=True, blank=True)
    
    pro = models.ForeignKey(ProductModel, on_delete=models.CASCADE, null=True, blank=True)

    product_name = models.CharField(max_length=150)
    product_code = models.CharField(max_length=50)
    product_description = models.TextField(null=True, blank=True)
    product_brand = models.CharField(max_length=50, null=True)
    product_category = models.CharField(max_length=50, null=True)
    product_hsn = models.CharField(max_length=50)
    product_barcode = models.CharField(max_length=50, null=True)
    product_packtype = models.CharField(choices=pack_type_choices, max_length=50, default="kg")
    pack_size = models.DecimalField(max_digits=5, decimal_places=3)
    
    mrp = models.IntegerField()
    sales_price = models.IntegerField()
    units = models.IntegerField(default=1)
    batch_no = models.CharField(max_length=50)
    discount_percentage_1 = models.IntegerField( null=True, blank=True)
    discount_amount_1 = models.IntegerField( null=True, blank=True)
    discount_percentage_2 = models.IntegerField( null=True, blank=True)
    discount_amount_2 = models.IntegerField( null=True, blank=True)
    discount_unit = models.IntegerField( null=True, blank=True)
    sgst_percentage = models.IntegerField( null=True, blank=True)
    sgst_amount = models.IntegerField( null=True, blank=True)
    cgst_percentage = models.IntegerField( null=True, blank=True)
    cgst_amount = models.IntegerField( null=True, blank=True)
    igst_percentage = models.IntegerField( null=True, blank=True)
    igst_amount = models.IntegerField( null=True, blank=True)
    total_amount = models.IntegerField( null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self.product:
            self.product_name = self.product.product.product_name
            self.product_code = self.product.product.product_code
            self.product_description = self.product.product.product_description
            self.product_hsn = self.product.product.product_hsn
            self.product_barcode = self.product.product.product_barcode
            self.product_packtype = self.product.product.product_packtype
            self.pack_size = self.product.pack_size
            self.mrp = self.product.mrp
            self.sales_price = self.product.sales_price
            self.batch_no = self.product.batch_no

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product_name} - {self.pack_size} kg/pck "

class ShippedFromModel(models.Model):
    add_1 = models.CharField(max_length=50)
    add_2 = models.CharField(max_length=50)
    contact = models.CharField(max_length=50)
    gstin = models.CharField(max_length=50)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.add_1}, {self.add_2}"


