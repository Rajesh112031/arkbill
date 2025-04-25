from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView


app_name = "billing"

urlpatterns = [
    ########
    path('temp/', TempTemplateView.as_view(), name='temp'),
    path('pdf/', PDFView.as_view(), name='pdf'),
    ########
    path('', IndexDashboardView.as_view(), name='dashboard'),
    path('login/', AdminLoginView.as_view(), name='login'),
    path('accounts/login/', AdminLoginView.as_view(), name='acc_login'),
    path('logout/', LogoutView.as_view(next_page = "billing:login"), name='logout'),
    path('productentry/', ProductEntryView.as_view(), name='product_entry'),
    path('productbrand/', ProductBrandView.as_view(), name='product_brand'),
    path('productcategory/', ProductCategoryView.as_view(), name='product_category'),
    path('product/', ProductView.as_view(), name='product_list'),
    path('customer/', CustomerView.as_view(), name='customer_list'),
    path('newcustomer/', CustomerEntryView.as_view(), name='customer_entry'),
    path('supplier/', SupplierView.as_view(), name='supplier_list'),
    path('newsupplier/', SupplierEntryView.as_view(), name='supplier_entry'),
    path('purchasedstock/', PurchasedStockView.as_view(), name='purchased_stock'),
    path('purchased/', PurchasedStockEntryView.as_view(), name='purchased_stock_entry'),
    
    path('bill/', BillView.as_view(), name='bill'),
    path('bills_entry/', BillEntryView.as_view(), name='bill_entry'),
   
    path('supplier_search/', SupplierSearchView.as_view(), name='supplier_search'),
    path('product_search/', ProductSearchView.as_view(), name='product_search'),
]
 