from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(ProductBrandModel)
admin.site.register(ProductCategoryModel)
admin.site.register(ProductModel)
admin.site.register(SupplierModel)
admin.site.register(CustomerModel)
admin.site.register(PurchaseStockModel)
admin.site.register(PurchaseStockProductModel)
admin.site.register(BillModel)
admin.site.register(BillProductModel)
admin.site.register(ShippedFromModel)