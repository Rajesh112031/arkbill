from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView


app_name = "billing"

urlpatterns = [
    ########
    path('temp/', TempTemplateView.as_view(), name='temp'),
    path('pdf/<int:pk>/', PDFView.as_view(), name='pdf'),
    # ########
    path('', IndexDashboardView.as_view(), name='dashboard'),
    path('login/', AdminLoginView.as_view(), name='login'),
    path('accounts/login/', AdminLoginView.as_view(), name='acc_login'),
    path('logout/', LogoutView.as_view(next_page = "billing:dashboard"), name='logout'),
    path('productentry/', ProductEntryView.as_view(), name='product_entry'),
    path('productbrand/', ProductBrandView.as_view(), name='product_brand'),
    path('productcategory/', ProductCategoryView.as_view(), name='product_category'),
    path('product/', ProductView.as_view(), name='product_list'),
    path('customer/', CustomerView.as_view(), name='customer_list'),
    path('newcustomer/', CustomerEntryView.as_view(), name='customer_entry'),
    path('customerupdate/<int:pk>/', CustomerUpdateView.as_view(), name='customer_update'),
    path('supplierupdate/<int:pk>/', SupplierUpdateView.as_view(), name='supplier_update'),
    path('supplier/', SupplierView.as_view(), name='supplier_list'),
    path('newsupplier/', SupplierEntryView.as_view(), name='supplier_entry'),
    path('purchasedstock/', PurchasedStockView.as_view(), name='purchased_stock'),
    path('purchasedstockbill/', PurchasedStockBillView.as_view(), name='purchased_stock_bill'),
    path('purchasedstockbill/<int:pk>/', PurchasedStockBillDetailView.as_view(), name='purchased_stock_bill_detail'),
    path('purchased/', PurchasedStockEntryView.as_view(), name='purchased_stock_entry'),
    path('purchase/pdf/<int:pk>/', generate_purchase_pdf, name='generate_purchase_pdf'),

    path('bill/', BillView.as_view(), name='bill'),
    path('bills_entry/', BillEntryView.as_view(), name='bill_entry'),
    path('bill_detail/<int:pk>/', BillDetailView.as_view(), name='bill_detail'),
   
    path('supplier_search/', SupplierSearchView.as_view(), name='supplier_search'),
    path('product_search/', ProductSearchView.as_view(), name='product_search'),
    path('customer_search/', CustomerSearchView.as_view(), name='customer_search'),
    path('product_available_search/', AvailableProductSearchView.as_view(), name='product_available_search'),

    path('shipping/', ShippingFromView.as_view(), name='shipping_view'),
    path('createshipping/', CreateShippingFromView.as_view(), name='shipping_create'),
    path('editshipping/', UpdateShippingFromView.as_view(), name='shipping_update'),

    path('estimationbills/', EstimationBillView.as_view(), name='estimation_bill'),
    path('estimationbill/<int:pk>/', EstimationDetailView.as_view(), name='estimation_detail'),
    path('estimationtobill/<int:pk>/', EstimationToBillView.as_view(), name='estimation_to_bill'),
  
    path('reportbill/', ReportBillManagementView.as_view(), name="report_bill"),
    path('reportstock/', ReportStockManagementView.as_view(), name="report_stock"),
    path('reportstockbill/', ReportStockBillManagementView.as_view(), name="report_stock_bill"),
    path('salesreport/', SalesreportBillManagementView.as_view(), name="sales_report"),
    path('purchasereport/', PurchaseReportView.as_view(), name="purchase_report"),
    path('stockmanufacture/', ReportStockManufactureManagementView.as_view(), name="report_stock_manufacture"),
    path('stockreport/', StockReportView.as_view(), name='stack_startment'),
    path('marginreport/', MarginReportView.as_view(), name='margin_report')

]
 