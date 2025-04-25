from django.views.generic import TemplateView, CreateView, ListView, View, DetailView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect,get_object_or_404,render
from django.db.models import Q
from django.utils.timezone import now
from datetime import datetime

from django.utils.dateparse import parse_date
from django.db.models import Sum
from django.db.models import F, ExpressionWrapper, FloatField, Case, When, Value
from django.db.models.functions import Coalesce

from .models import *
from .forms import *    

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle   

from math import ceil
import os

import math

#################################################
class TempTemplateView(TemplateView):
    template_name = "send.html"
###########################################
    
class IndexDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"
    
class AdminLoginView(LoginView):
    success_url = reverse_lazy("billing:dashboard")
    
    def get_success_url(self):
        return self.success_url
################
class StockSearchView(LoginRequiredMixin, ListView):
    model = ProductModel
    context_object_name = "stocks"

    def get_queryset(self):
        query = self.request.GET.get("query", "")
        if query:
            return ProductModel.objects.filter(product_name__icontains=query)[:10]
        # print(ProductModel.objects.all()[:10])
        return ProductModel.objects.all()[:10]
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest': 
            data = list(self.get_queryset().values('id', 'product_name', 'product_code'))
            return JsonResponse(data, safe=False) 
        return redirect("billing:dashboard")
##############
class ProductBrandView(LoginRequiredMixin, CreateView):
    model = ProductBrandModel
    fields = "__all__"
    success_url = reverse_lazy("billing:product_entry")
    
    def render_to_response(self, context, **response_kwargs):
        return self.success_url
    
class ProductCategoryView(LoginRequiredMixin, CreateView):
    model = ProductCategoryModel
    fields = "__all__"
    success_url = reverse_lazy("billing:product_entry")
    
    def render_to_response(self, context, **response_kwargs):
        return self.success_url
    
class ProductEntryView(LoginRequiredMixin, CreateView):
    template_name = "product/productentry.html"
    form_class = ProductForm
    success_url = reverse_lazy("billing:product_list")
    
class ProductView(LoginRequiredMixin, ListView):
    template_name = "product/productview.html"
    model = ProductModel
    context_object_name = "products"
    paginate_by = 20
    
# class BrandView(LoginRequiredMixin, ListView):
#     template_name = "product/productview.html"
#     model = ProductBrandModel
#     context_object_name = "brands"
#     paginate_by = 20
    
# class CategoryView(LoginRequiredMixin, ListView):
#     template_name = "product/productview.html"
#     model = ProductCategoryModel
#     context_object_name = "categories"
#     paginate_by = 20
    
class CustomerView(LoginRequiredMixin, ListView):
    template_name = "customer/customer.html"
    model = CustomerModel
    fields = "__all__"
    paginate_by = 20
    context_object_name = "customers"

class CustomerEntryView(LoginRequiredMixin, CreateView):
    template_name = "customer/newcustomer.html"
    form_class = CustomerForm
    success_url = reverse_lazy("billing:customer_list")
    
class SupplierView(LoginRequiredMixin, ListView):
    template_name = "supplier/supplier.html"
    model = SupplierModel
    fields = "__all__"
    paginate_by = 20
    context_object_name = "suppliers"

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "customer/editcustomer.html"
    model = SupplierModel
    fields = "__all__"
    success_url = reverse_lazy("billing:supplier_list")

class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "Supplier/editsupplier.html"
    model = SupplierModel
    fields = "__all__"
    success_url = reverse_lazy("billing:supplier_list")


    # def form_valid(self, form):
    #     return super().form_valid(form)

class SupplierEntryView(LoginRequiredMixin, CreateView):
    template_name = "Supplier/newSupplier.html"
    form_class = SupplierForm
    success_url = reverse_lazy("billing:supplier_list")
    
class PurchasedStockEntryView(LoginRequiredMixin, CreateView):
    template_name = "purchasestock/purchaseentry.html"
    form_class = PurchasedStockEntryForm
    success_url = reverse_lazy("billing:purchased_stock")
    
    def form_valid(self, form):

        form.instance.supplier = SupplierModel.objects.get(supplier_id = self.request.POST.get("supplier_id")) or None
        
        bill_id = now().strftime("%Y%m%d%H%M%S")
        while PurchaseStockModel.objects.filter(purchase_bill_id=bill_id).exists():
            bill_id = str(int(bill_id) + 1)
        form.instance.purchase_bill_id = bill_id
        form.save()
        
        index = self.request.POST.get("indexValue", None)
        if index is None:
            return super().form_invalid(form)
        
        for i in range(1, int(index)+1):
            manufacture_date_str = self.request.POST.get(f"manufacture_{i}", "").strip()
            expiring_date_str = self.request.POST.get(f"expiring_{i}", "").strip()

            PurchaseStockProductModel.objects.create(purchase_stock = PurchaseStockModel.objects.get(purchase_bill_id = bill_id),
                                                        product = ProductModel.objects.get(id = int(self.request.POST.get(f"product_id_{i}"))),
                                                        hsn = self.request.POST.get(f"hsn_{i}", ""),
                                                        pack_size = self.request.POST.get(f"pack_size_{i}", ""),
                                                        mrp = self.request.POST.get(f"mrp_{i}", ""),
                                                        sales_price = self.request.POST.get(f"sales_price_{i}", ""),
                                                        units = self.request.POST.get(f"quantity_{i}", ""),
                                                        batch_no = self.request.POST.get(f"batch_{i}", ""),
                                                        discount_percentage_1 = self.request.POST.get(f"discount_percentage_{i}", "0").strip() or 0,
                                                        discount_amount_1 = self.request.POST.get(f"discount_amount_{i}", "0").strip() or 0,
                                                        discount_percentage_2 = self.request.POST.get(f"added_discount_{i}", "0").strip() or 0,
                                                        discount_amount_2 = self.request.POST.get(f"added_discount_amount_{i}", "0").strip() or 0,
                                                        discount_unit = self.request.POST.get(f"free_quantity_{i}", "0").strip() or 0,
                                                        sgst_percentage = self.request.POST.get(f"sgst_{i}", "0").strip() or 0,
                                                        sgst_amount = self.request.POST.get(f"sgst_amount_{i}", "0").strip() or 0,
                                                        cgst_percentage = self.request.POST.get(f"cgst_{i}", "0").strip() or 0,
                                                        cgst_amount = self.request.POST.get(f"cgst_amount_{i}", "0").strip() or 0,
                                                        igst_percentage = self.request.POST.get(f"igst_{i}", "0").strip() or 0,
                                                        igst_amount = self.request.POST.get(f"igst_amount_{i}", "0").strip() or 0,
                                                        manufacturing = datetime.strptime(manufacture_date_str, "%Y-%m-%d") if manufacture_date_str else None,
                                                        expiring = datetime.strptime(expiring_date_str, "%Y-%m-%d") if expiring_date_str else None,
                                                        total_quantity = self.request.POST.get(f"total_quantity_{i}", ""),
                                                        total_price = self.request.POST.get(f"total_price_{i}", ""),
                                                        totalTax = self.request.POST.get(f"totalTax_{i}", ""),
                                                        grandTotal = self.request.POST.get(f"grandTotal_{i}", ""),
                                                    )
            
        return redirect(self.success_url)
    
class PurchasedStockView(LoginRequiredMixin, ListView):
    template_name = "purchasestock/purchased.html"
    model = PurchaseStockProductModel
    paginate_by = 20
    context_object_name = "products"

class PurchasedStockBillView(LoginRequiredMixin, ListView):
    template_name = "purchasestock/purchasedbill.html"
    model = PurchaseStockModel
    paginate_by = 20
    context_object_name = "productbills"
    
class PurchasedStockBillDetailView(LoginRequiredMixin, DetailView):
    template_name = "purchasestock/purchasebilldetail.html"
    model = PurchaseStockModel
    context_object_name = "detail"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        purchase_stock = self.get_object()
        context["products"] = PurchaseStockProductModel.objects.filter(purchase_stock=purchase_stock)
        return context
    
class SupplierSearchView(LoginRequiredMixin, ListView):
    model = SupplierModel
    context_object_name = "supplier"

    def get_queryset(self):
        query = self.request.GET.get("query", "")
        if query:
            return SupplierModel.objects.filter(
                Q(supplier_name__icontains=query) | Q(supplier_id__icontains=query)
            ).only("supplier_id",
                   "id",
                   "supplier_name",
                   "supplier_phone",
                   "supplier_state",
                   "supplier_account_balance")[:10]
        # print(ProductModel.objects.all()[:10])
        return SupplierModel.objects.all().only("supplier_id",
                   "id",
                   "supplier_name",
                   "supplier_phone",
                   "supplier_state",
                   "supplier_account_balance")[:10]
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest': 
            data = list(self.get_queryset().values())
            return JsonResponse(data, safe=False) 
        return redirect("billing:dashboard")

class ProductSearchView(LoginRequiredMixin, ListView):
    model = ProductModel
    context_object_name = "supplier"

    def get_queryset(self):
        query = self.request.GET.get("query", "")
        if query:
            return ProductModel.objects.filter(
                Q(product_name__icontains=query) | Q(product_code__icontains=query)
            ).values("product_name",
                "id",
                "product_code",
                "product_hsn",
                "product_barcode",
                "product_packtype",
                "pack_size",
                "purchase_stock",  
                "mrp",
                "sales_price",
                "units",
                "manufacturing",
                "expiring")[:10]
        # print(ProductModel.objects.all()[:10])
        return ProductModel.objects.all().only("product_name",
            "id",
            "product_code",
            "product_hsn",
            "product_barcode",
            "product_packtype",
            "pack_size",
            "purchase_stock",  
            "mrp",
            "sales_price",
            "units",
            "manufacturing",
            "expiring")[:10]
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest': 
            data = list(self.get_queryset().values())
            return JsonResponse(data, safe=False) 
        return redirect("billing:dashboard")
    
    
        # Q(product__product_name__icontains=query) | Q(product__product_code__icontains=query)
        #     ).only("product",
        #            "hsn",
        #            "pack_size",
        #            "mrp",
        #            "sales_price",
        #            "batch_no",
        #            "manufacturing",
        #            "expiring",
        #            "total_quantity")[:10]

class AvailableProductSearchView(LoginRequiredMixin, ListView):
    model = PurchaseStockProductModel
    context_object_name = "supplier"

    def get_queryset(self):
        query = self.request.GET.get("query", "")
        queryset = PurchaseStockProductModel.objects.select_related("product")
        
        if query:
            queryset = queryset.filter(
                Q(product__product_name__icontains=query) |
                Q(product__product_code__icontains=query) 
            )

        return queryset.values(
            "id",
            "purchase_stock",
            "product__product_name",
            "product__product_code",
            "product__product_hsn",
            "product__product_barcode",
            "product__product_packtype",
            "hsn",
            "pack_size",
            "mrp",
            "sales_price",
            "units",
            "batch_no",
            "manufacturing",
            "expiring"
        )[:10]

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest': 
            data = list(self.get_queryset())  # No need for `.values()` here again
            return JsonResponse(data, safe=False)
        return redirect("billing:dashboard")
        
class CustomerSearchView(LoginRequiredMixin, ListView):
    model = CustomerModel
    context_object_name = "customer"

    def get_queryset(self):
        query = self.request.GET.get("query", "")
        if query:
            return CustomerModel.objects.filter(
                Q(customer_name__icontains=query) | Q(customer_id__icontains=query)
                # Q(SELECT * FROM "CUSTOMER_NAME" CONTAINS "query" OR SELECT * FROM "CUSTOMER_ID" CONTAINS "query")
            ).only("customer_name",
                   "id",
                   "customer_id",
                   "customer_hsn",
                   "customer_barcode",
                   "customer_packtype",
                   "pack_size")[:10]
        # print(CustomerModel.objects.all()[:10])
        return CustomerModel.objects.all().only("customer_name",
                   "id",
                   "customer_id",
                   "customer_hsn",
                   "customer_barcode",
                   "customer_packtype",
                   "pack_size")[:10]
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest': 
            data = list(self.get_queryset().values())
            return JsonResponse(data, safe=False) 
        return redirect("billing:dashboard")
    
    
        # Q(product__product_name__icontains=query) | Q(product__product_code__icontains=query)
        #     ).only("product",
        #            "hsn",
        #            "pack_size",
        #            "mrp",
        #            "sales_price",
        #            "batch_no",
        #            "manufacturing",
        #            "expiring",
        #            "total_quantity")[:10]
        
class BillView(LoginRequiredMixin, ListView):
    template_name = "bill/billview.html"
    model = BillModel
    paginate_by = 20
    context_object_name = "bills"
    
class BillDetailView(LoginRequiredMixin, DetailView):
    template_name = "bill/billdetail.html"
    model = BillModel
    context_object_name = "detail"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = BillProductModel.objects.filter(bill=self.get_object())
        return context
       
class BillEntryView(LoginRequiredMixin, CreateView):
    template_name = "bill/billentry.html"
    form_class = BillEntryForm
    success_url = reverse_lazy("billing:bill")
    
    def form_valid(self, form):

        form.instance.customer = CustomerModel.objects.get(customer_id = self.request.POST.get("customer_id")) or None

        bill_id = now().strftime("%Y%m%d%H%M%S")
        while BillModel.objects.filter(bill_id=bill_id).exists():
            bill_id = str(f"b{int(bill_id) + 1}")
        form.instance.bill_id = bill_id
        form.save()
        
        index = self.request.POST.get("indexValue", None)
        if index is None:
            return super().form_invalid(form)
        
        for i in range(1, int(index)+1):
            BillProductModel.objects.create(bill = BillModel.objects.get(bill_id=bill_id),
                                            product = PurchaseStockProductModel.objects.get(id = int(self.request.POST.get(f"product_id_{i}"))),
                                            pack_size = self.request.POST.get(f"pack_size_{i}"),
                                            mrp = self.request.POST.get(f"mrp_{i}"),
                                            sales_price = self.request.POST.get(f"sales_price_{i}"),
                                            units = self.request.POST.get(f"quantity_{i}"),
                                            batch_no = self.request.POST.get(f"batch_{i}"),
                                            discount_amount_1 = self.request.POST.get(f"discount_amount_{i}", "0").strip() or 0,
                                            discount_percentage_2 = self.request.POST.get(f"added_discount_{i}", "0").strip() or 0,
                                            discount_amount_2 = self.request.POST.get(f"added_discount_amount_{i}", "0").strip() or 0,
                                            discount_unit = self.request.POST.get(f"free_quantity_{i}", "0").strip() or 0,
                                            sgst_percentage = self.request.POST.get(f"sgst_{i}", "0").strip() or 0,
                                            sgst_amount = self.request.POST.get(f"sgst_amount_{i}", "0").strip() or 0,
                                            cgst_percentage = self.request.POST.get(f"cgst_{i}", "0").strip() or 0,
                                            cgst_amount = self.request.POST.get(f"cgst_amount_{i}", "0").strip() or 0,
                                            igst_percentage = self.request.POST.get(f"igst_{i}", "0").strip() or 0,
                                            igst_amount = self.request.POST.get(f"igst_amount_{i}", "0").strip() or 0,
                                            total_amount = self.request.POST.get(f"grandTotal_{i}", "0").strip() or 0,
                                        )
            
        return redirect(self.success_url)


def generate_purchase_pdf(request, pk):
    try:
        purchase = PurchaseStockModel.objects.select_related('supplier').get(pk=pk)
    except PurchaseStockModel.DoesNotExist:
        return HttpResponse("Invoice not found", status=404)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=invoice_{purchase.invoice_no}.pdf'
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    font_family = "Helvetica"
    font_family_bold = "Helvetica-Bold"

    logo_path = os.path.join(os.path.dirname(__file__), "static/asset/images/ARK_logo-01.png")

    def draw_watermark(canvas_obj):
        canvas_obj.saveState()
        canvas_obj.setFont(font_family_bold, 100)
        canvas_obj.setFillGray(0.95, 0.95)
        canvas_obj.drawCentredString(width / 2, height / 2 + 30, "ark")
        canvas_obj.setFont(font_family_bold, 30)
        canvas_obj.drawCentredString(width / 2, height / 2 - 10, "AGENCY")
        canvas_obj.setFont(font_family, 12)
        canvas_obj.drawCentredString(width / 2, height / 2 - 30, "Complete Solution for Pets")
        canvas_obj.restoreState()

    def draw_header(canvas_obj):
        draw_watermark(canvas_obj)
        canvas_obj.drawImage(logo_path, x=0, y=height - 130, width=207, height=130, mask="auto")
        canvas_obj.setFont(font_family_bold, 16)
        canvas_obj.setFillColor(colors.orange)
        canvas_obj.drawString(200, height - 40, "ARK AGENCY")
        canvas_obj.setFont(font_family, 10)
        canvas_obj.setFillColor(colors.black)

        y_addr = height - 55
        for line in [
            "1-145, South Vattam, Pandaravillai,",
            "Thiruvithancode post, K.K Dist-629174, Tamil Nadu[33]"
        ]:
            canvas_obj.drawString(200, y_addr, line.strip())
            y_addr -= 12

        y_contact = height - 55
        for line in [
            "+91 9999999999", "+91 9999999999",
            "xyz@mail.com", "GSTIN: 33XYSTAIMNDLOOOKKIO"
        ]:
            canvas_obj.drawRightString(width - 40, y_contact, line.strip())
            y_contact -= 12

        canvas_obj.setFont(font_family_bold, 10)
        canvas_obj.drawString(30, height - 150, "Invoice No:")
        canvas_obj.setFont(font_family, 9)
        canvas_obj.drawString(100, height - 150, purchase.invoice_no)
        canvas_obj.setFont(font_family_bold, 10)
        canvas_obj.drawString(250, height - 150, "Date:")
        canvas_obj.setFont(font_family, 9)
        canvas_obj.drawString(280, height - 150, purchase.invoice_date.strftime('%Y-%m-%d'))
        canvas_obj.setFont(font_family_bold, 10)
        canvas_obj.drawString(450, height - 150, "Tax Type:")
        canvas_obj.setFont(font_family, 9)
        canvas_obj.drawString(510, height - 150, "Inclusive")

    def draw_footer(canvas_obj, y_pos):
        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.drawString(30, y_pos, "Our Bank Details:")
        canvas_obj.setFont("Helvetica", 8)
        lines = [
            "Account Name: ARK AGENCY",
            "Account No: WOUIUGHEGHTOJRT",
            "Bank Name: xyz BANK",
            "Branch: TAMIL NADU",
            "IFSC Code: 123693VCSDIFIONI"
        ]
        for i, line in enumerate(lines):
            canvas_obj.drawString(30, y_pos - ((i + 1) * 12), line)
        canvas_obj.setFont("Helvetica-Bold", 9)
        canvas_obj.drawRightString(width - 40, y_pos - 72, "Authorized Signatory")

    headers = ["Sn", "Product Name", "HSNC", "MRP", "Rate", "Disc.", "Qnt", "CGST", "SGST", "IGST", "Total"]
    all_rows = []
    for idx, item in enumerate(purchase.purchasestockproductmodel_set.all(), start=1):
        row = [
            str(idx),
            item.product.product_name if item.product else '',
            item.hsn or '',
            f"{item.mrp:.2f}",
            f"{item.buy_price:.2f}",
            f"{item.discount_amount_1:.2f}",
            str(item.units),
            f"{item.cgst_amount:.2f}",
            f"{item.sgst_amount:.2f}",
            f"{item.igst_amount:.2f}",
            f"{item.total_price:.2f}" if item.total_price else "0.00",
        ]
        all_rows.append(row)

    rows_per_page = 20
    total_pages = ceil(len(all_rows) / rows_per_page)

    for page in range(total_pages):
        if page > 0:
            p.showPage()
        draw_header(p)

        start = page * rows_per_page
        end = start + rows_per_page
        page_data = [headers] + all_rows[start:end]

        table = Table(page_data, colWidths=[20, 90, 60, 45, 45, 45, 45, 45, 45, 45, 45])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, 0), font_family_bold),
            ('FONTNAME', (0, 1), (-1, -1), font_family),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ]))

        table.wrapOn(p, width, height)
        table_height = table._height
        y_table = height - 210  # Adjusted for header space
        table.drawOn(p, 30, y_table - table_height)

        if page == total_pages - 1:
            y_footer = 100
            p.setFont("Helvetica-Bold", 9)
            p.drawString(30, y_footer + 60, "GST Summary")
            p.drawString(480, y_footer + 60, "Discount:")
            p.setFont("Helvetica", 8)
            p.drawString(30, y_footer + 48, f"No of Qnt: {purchase.total_units}")
            p.drawString(480, y_footer + 48, f"SubTotal: {purchase.total_amount - purchase.total_tax_amount:.2f}")
            p.drawString(480, y_footer + 36, f"Grand Total: {purchase.total_amount:.2f}")
            p.drawString(480, y_footer + 24, "Total Paid: 0")
            p.drawString(480, y_footer + 12, "Balance: 0")

            draw_footer(p, y_footer)

    p.save()
    return response

class PDFView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        ship_add = ShippedFromModel.objects.filter(status=True).first()
        bill_main = BillModel.objects.get(pk=kwargs.get("pk"))
        products = BillProductModel.objects.filter(bill=bill_main)

        # create httpsresponse content type set to pdf
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = "inline; filename='invoice.pdf'"
        
        # create canvas
        c = canvas.Canvas(response, pagesize=A4)
        
        width, height = A4
        # print("width: ", width, "height: ", height) 
        # width:  595.2755905511812 height:  841.8897637795277
        
        ######################################################################
        ####################           :)             ########################
        ######################################################################
        
        # root values
        # width, height = 595, 841
        
        font_family = "Helvetica"
        font_family_bold = "Helvetica-Bold"
        font_extra_large = 18
        font_large = 11
        font_medium = 10
        font_small = 8
        line_spacing = 15
        
        margin_page_x = 35
        margin_page_y = 20
        margin_page_x_text = 5

        table_border = 1
        table_corner = [2,2,2,2]
        
        margin_x = 60
        margin_y = 30
        
        y_span = 0
        
        #####################################
        address_head = "ARK AGENCY"
        address_body = """1-145, South Vattam, Pandaravillai,
                            Thiruvithancode post,
                            K.K Dist-629174,
                            Tamil Nadu[33]"""

        contact_details = """+91 9999999999
                                +91 9999999999
                                xyz@mail.com
                                GSTIN: 33XYSTAIMNDLOOOKKIO"""
        
        shipped_from_address = f"""Shipped From:
                            ARK AGENCY STORE
                            {ship_add.add_1},
                            {ship_add.add_2}.
                            Contact No: {ship_add.contact}
                            GSTIN: {ship_add.gstin}"""
        
        billed_to_address = f"""Billed To:
                            {bill_main.customer.customer_name[:10]}
                            {bill_main.customer.customer_address[:30]},
                            {bill_main.customer.customer_state}.
                            Contact No: {bill_main.customer.customer_phone}
                            GSTIN: {bill_main.customer.customer_gst_or_uid}"""
        
        invoice_heading = f"""Invoice of (RS)
                            Rs.{bill_main.total_amount}
                            Invoice.No. {bill_main.invoice_no}
                            Date: {bill_main.invoice_date}
                            Tax-type: {'Inclusive' if bill_main.tax_type else 'Exclusive'}"""
        
        bank_details = """Our Bank Details:
                        Account Name :  ARK AGENCY
                        Account No      :  WOIUGEHGHTOJRT
                        Bank Name      :  xyz bANK
                        Branch Name   :  TAMIL NADU
                        IFSC Code       :  123693VCSDFIONI
                        """
        #####################################
        page_no = 1
        ###################################################################################
        
        def description_formatter(des: str) -> str:
            # Split the description into words
            words = des.split()
            
            # Initialize variables
            line = ""
            formatted_description = []
            
            for word in words:
                # Check if adding the next word would exceed the 32 character limit
                if len(line) + len(word) + 1 <= 32:
                    # Add the word to the current line
                    if line:
                        line += " " + word  # Add space before the word if it's not the first word
                    else:
                        line = word
                else:
                    # If the line exceeds 32 characters, add it to the formatted list and start a new line
                    formatted_description.append(line)
                    line = word  # Start the new line with the current word
            
            # Add the last line to the formatted description
            if line:
                formatted_description.append(line)
            
            # Join the lines with newline characters
            return "\n".join(formatted_description)
        ###################################################################################
        # set title
        c.setTitle("Invoice")
        
        # from ark_main import settingsD:\cod\zoro\ark_billing\ark_main 2\billing\static\asset\images\ARK_logo-01.png
        logo_path = os.path.join(os.path.dirname(__file__), r"static/asset/images/ARK_logo-01.png")
        # logo_path = os.path.join(settings.BASE_DIR, "ARK_logo-01.png")
        
        # img bg
        def draw_bg():
            c.setFillAlpha(0.15)
            c.drawImage(logo_path, x=65, y=220, height=350, width=450, mask="auto")
            c.setFillAlpha(1)
        
        # img margin top
        # c.drawImage(r"c:\Users\SUPER-POTATO\Desktop\Picture11.png", x=0, y=height - margin_page_y)
        
        def draw_navbar():
            # img logo
            c.drawImage(logo_path, x=0, y=715, width=207, height=130)
            
            # address page top
            c.setFont(font_family_bold, font_extra_large)
            c.setFillColor(colors.orange)
            c.drawString( 200, 800, address_head)
            c.setFillColor(colors.black) 
            
            c.setFont(font_family, font_large)
            temp_spacing = 800 
            for line in address_body.splitlines():
                c.drawString(200, temp_spacing:= temp_spacing - line_spacing , line.strip())
            
            temp_spacing = 800 
            for line in contact_details.splitlines():
                c.drawRightString(width - 35, temp_spacing:= temp_spacing - line_spacing , line.strip())

        draw_bg()
        draw_navbar()

        # shipping addresses
        temp_spacing = 700
        for i, line in enumerate(shipped_from_address.splitlines()):
            if i == 1:
                c.setFont(font_family_bold, font_medium)
                c.drawString(margin_page_x, temp_spacing:= temp_spacing - line_spacing , line.strip())
            else:
                c.setFont(font_family, font_medium)
                c.drawString(margin_page_x, temp_spacing:= temp_spacing - line_spacing , line.strip())
        
        temp_spacing = 700
        for i, line in enumerate(billed_to_address.splitlines()):
            if i == 1:
                c.setFont(font_family_bold, font_medium)
                c.drawString(margin_page_x + 200, temp_spacing:= temp_spacing - line_spacing , line.strip())
            else:
                c.setFont(font_family, font_medium)
                c.drawString(margin_page_x + 200, temp_spacing:= temp_spacing - line_spacing , line.strip())
        
        
        # invoice heading
        temp_spacing = 700
        for i, line in enumerate(invoice_heading.splitlines()):
            if i == 1:
                c.setFont(font_family_bold, font_extra_large)
                c.setFillColor(colors.orange)
                c.drawRightString(width-35, temp_spacing:= temp_spacing - line_spacing -5 , line.strip())
                c.setFillColor(colors.black)
            else:
                c.setFont(font_family, font_medium)
                c.drawRightString(width-35, temp_spacing:= temp_spacing - line_spacing , line.strip())
        

        # Table
        invoice_data = [
            # table head
            ["Sn\nNo.", "Product Name", "HSNC", "MRP", "Rate", "Disc.", "Qnt", "CGST", "SGST", "IGST", "Total"],
        ]

        cgst_total = 0
        sgst_total = 0
        igst_total = 0
        
        for i, product in enumerate(products, 1):
            invoice_data.append([
                i, 
                description_formatter(product.product_name), 
                product.product_hsn, 
                product.mrp, 
                product.sales_price, 
                product.discount_amount_1+product.discount_amount_2, 
                product.discount_unit+product.units,
                product.cgst_amount,
                product.sgst_amount,
                product.igst_amount,
                product.total_amount,
            ],
            )
            cgst_total += product.cgst_amount
            sgst_total += product.sgst_amount
            igst_total += product.igst_amount
            cgst_percentage = product.cgst_amount
            sgst_percentage = product.sgst_amount
            igst_percentage = product.igst_amount

        # print(invoice_data)

        # 00 10 20 30 40 50 60 70 80 90 100
        # 01 11 21 31 41 51 61 71 81 91 101
        
        # .. .. .. .. .. .. -2-2 -1-2
        # .. .. .. .. .. .. -2-1 -1-1
        
        # create table
        table = Table(invoice_data, colWidths=[20, 145, 35, 45, 40, 40, 35, 40, 40, 40 ,45])
        
        # Add styles to the table
        style = TableStyle([
            ('GRID', (0, 0), (-1, -1), table_border, colors.black),
            # alignments
            # ('VALIGN', (0, 2), (-1, -5), 'TOP'),   
            # ('ALIGN', (2, 2), (-1, -5), 'CENTER'),   
            # ('ALIGN', (2, 2), (-1, -5), 'CENTER'),   
            # ('BOTTOMPADDING', (0, 0), (-1, 0), 10),  
            # font
            ('FONTNAME', (0, 0), (-1, 0), font_family_bold),  
            ('FONTNAME', (2, 2), (-1, -1), font_family),  
            ('FONTSIZE', (0, 0), (-1, -1), font_small),   
            # border
            ('ROUNDEDCORNERS', table_corner),
        ])

        table.setStyle(style)
        table_width, table_height = table.wrapOn(c, width, height)

        ################################

        # Page and layout configurations
        page_height = 505
        max_table_height_per_page = 345
        initial_y_position = 500

        # Calculate the number of rows per page
        rows_per_page = 10 
        total_rows = len(invoice_data)
        page_no = ceil(total_rows / rows_per_page)

        # Draw the table across pages
        current_row = 0
        row_start = 0
        row_end = total_rows

        if page_no >= 2:
            for p in range(page_no):
                draw_bg()
                draw_navbar()

                row_start = current_row
                row_end = total_rows

                if current_row >= total_rows:
                    page_data = invoice_data[row_start:row_end]
                    current_row = row_end

                    table = Table(page_data, colWidths=[20, 145, 35, 45, 40, 40, 35, 40, 40, 40, 45])
                    table.setStyle(style)
                    table_width, table_height = table.wrapOn(c, width, height)

                else:
                    if p == 0:
                        y_position = initial_y_position - table_height + 91
                    else:
                        y_position = initial_y_position - table_height + 191
                    table.drawOn(c, margin_page_x, y_position)
                    if table_height > 400:
                        c.showPage()          
                    break

                while table_height > 400:

                    page_data = invoice_data[row_start:row_end]
                    current_row = row_end

                    table = Table(page_data, colWidths=[20, 145, 35, 45, 40, 40, 35, 40, 40, 40, 45])
                    table.setStyle(style)

                    table_width, table_height = table.wrapOn(c, width, height)

                    print(table_height)
                
                    row_end -= 1

                if p == 0:
                    y_position = initial_y_position - table_height + 91
                else:
                    y_position = initial_y_position - table_height + 191
                table.drawOn(c, margin_page_x, y_position)

                if table_height > 400:
                    c.showPage() 
            
            draw_bg()
            draw_navbar()

        if page_no == 1:
            table.drawOn(c, margin_page_x, 500 - table_height + 91)

        # GST SUMMARY
        c.setFont(font_family, font_medium)

        if igst_total > 0:
            gst_summary = [
                # table head
                ["GST Summary", "", f"Discount: {bill_main.total_discount_amount}", "", "", ""],
                # table body
                ["No fo Qnt:", f"{bill_main.total_units}", "SubTotal:", f"{bill_main.total_amount-bill_main.total_tax_amount}", "Bill Discount", f"{bill_main.bill_discount_amount}"],
                ["CGST", "SGST", "CGST", "", "Grand Total", f"{bill_main.total_amount}"],
                ["0%", "0%", "IGST", f"{igst_total}", "Total paid", f"{bill_main.total_paid}"],
                ["0", "0", "Total", f"{igst_total}", "Balance", f"{bill_main.balance}"],
            ]

        else:
            gst_summary = [
                # table head
                ["GST Summary", "", f"Discount: {bill_main.total_discount_amount}", "", "", ""],
                # table body
                ["No fo Qnt:", f"{bill_main.total_units}", "SubTotal:", f"{bill_main.total_amount-bill_main.total_tax_amount}", "Bill Discount", f"{bill_main.bill_discount_amount}"],
                ["CGST", "SGST", "CGST", f"{cgst_total}", "Grand Total", f"{bill_main.total_amount}"],
                [f"{cgst_percentage}%", f"{sgst_percentage}%", "SGST", f"{sgst_total}", "Total paid", f"{bill_main.total_paid}"],
                [f"{cgst_total}", f"{sgst_total}", "Total", f"{cgst_total+sgst_total}", "Balance", f"{bill_main.balance}"],
            ]
        
        # GST summary table
        gst_table = Table(gst_summary, colWidths=[87.5, 87.5, 87.5 ,87.5 ,87.5 ,87.5])
        gst_style = TableStyle([
            # Table SPAN
            ('SPAN', (0,0), (1,0)), ('SPAN', (2,0),(5,0)),
            # Alignments
            ('ALIGN', (0,0), (1,0), 'CENTER'), ('ALIGN', (2,0),(5,0), 'CENTER'),
            ('ALIGN', (0,1), (0,1), 'LEFT'),
            ('ALIGN', (1,1), (1,1), 'RIGHT'),
            ('ALIGN', (0,2), (1,4), 'CENTER'),
            ('ALIGN', (2,1), (3,4), 'LEFT'),
            ('ALIGN', (4,1), (4,4), 'LEFT'),
            ('ALIGN', (3,1), (3,4), 'RIGHT'),
            ('ALIGN', (5,1), (5,4), 'RIGHT'),
            # box
            ('BOX', (0,0), (-1,-1), table_border, colors.black),
            ('BOX', (0,0), (5,0), table_border, colors.black),
            ('BOX', (0,0), (1,4), table_border, colors.black),
            ('BOX', (2,0), (5,4), table_border, colors.black),
            ('BOX', (2,1), (3,4), table_border, colors.black),
            ('BOX', (0,1), (1,1), table_border, colors.black),
            # font
            ('FONT', (0,0), (5,0), font_family_bold, font_medium),
            ('FONT', (1,1), (1,1), font_family_bold, font_medium),
            ('FONT', (1,1), (1,1), font_family_bold, font_medium),
            ('FONT', (5,1), (5,4), font_family_bold, font_medium),
            # rouncorners
            ('ROUNDEDCORNERS', table_corner),
        ])
        gst_table.setStyle(gst_style)
        
        # Draw gst table
        gst_table.wrapOn(c, width, 0)
        gst_table.drawOn(c, margin_page_x, 140)

        
        # Bank details
        temp_spacing = 120
        c.setFont(font_family, font_medium)
        for i, line in enumerate(bank_details.splitlines()):
            c.drawString( margin_page_x, temp_spacing:= temp_spacing - line_spacing , line.strip())
        
        # Authorized signatory
        c.setFont(font_family_bold, font_medium)
        c.drawRightString(width - 35, temp_spacing:= temp_spacing + line_spacing, "Authorized Signatory")


        ######################################################################

        # finishing canvas
        c.showPage()
        c.save()
        return response

class CreateShippingFromView(LoginRequiredMixin, CreateView):
    template_name = "shipping/newshippingadd.html"
    model = ShippedFromModel
    fields = "__all__"
    success_url = reverse_lazy("billing:shipping_view")

class ShippingFromView(LoginRequiredMixin, ListView):
    template_name = "shipping/shippingadd.html"
    model = ShippedFromModel
    context_object_name = "address"

class UpdateShippingFromView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        ShippedFromModel.objects.filter(status=True).update(status=False)

        address = ShippedFromModel.objects.get(id=self.request.POST.get("id"))
        address.status = True
        address.save()
        return redirect(reverse("billing:shipping_view"))


# class PDFView(View):
#     def get(self, request, *args, **kwargs):
        
#         # create httpsresponse content type set to pdf
#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = "inline; filename='invoice.pdf'"
        
#         # create canvas
#         c = canvas.Canvas(response, pagesize=A4)
        
#         width, height = A4
#         # print("width: ", width, "height: ", height) 
#         # width:  595.2755905511812 height:  841.8897637795277
        
#         ######################################################################
#         ####################           :)             ########################
#         ######################################################################
        
#         # root values
#         # width, height = 595, 841
        
#         font_family = "Helvetica"
#         font_family_bold = "Helvetica-Bold"
#         font_medium = 10
#         font_extra_large = 18
#         font_large = 13
#         font_small = 8
#         line_spacing = 15
        
#         margin_page_x = 35
#         margin_page_y = 20
#         margin_page_x_text = 5

#         table_border = 1
#         table_corner = [2,2,2,2]
        
#         margin_x = 60
#         margin_y = 30
        
#         y_span = 0
        
#         #####################################
#         address_head = "ARK AGENCY"
#         address_body = """1-145, South Vattam, Pandaravillai,
#                             Thiruvithancode post,
#                             K.K Dist-629174,
#                             Tamil Nadu[33]"""

#         contact_details = """+91 9999999999
#                                 +91 9999999999
#                                 xyz@mail.com
#                                 GSTIN: 33XYSTAIMNDLOOOKKIO"""
        
#         shipped_from_address = """Shipped From:
#                             ARK AGENCY STORE
#                             Pandaravilai,
#                             Thiruvithamcode post.
#                             Contact No: +919000000
#                             GSTIN: UGFDSOHDOWFHOEH"""
        
#         billed_to_address = """Billed To:
#                             ARK AGENCY STORE
#                             Pandaravilai,
#                             Thiruvithamcode post.
#                             Contact No: +919000000
#                             GSTIN: UGFDSOHDOWFHOEH"""
        
#         invoice_heading = """Invoice of (RS)
#                             1234324
#                             Bill.No. XYZ-2025-12345
#                             Date: 01/01/2025
#                             Tax-type: Exclusive"""
        
#         bank_details = """Our Bank Details:
#                         Account Name :  ARK AGENCY
#                         Account No   :  WOIUGEHGHTOJRT
#                         Bank Name    :  xyz bANK
#                         Branch Name  :  TAMIL NADU
#                         IFSC Code    :  123693VCSDFIONI
#                         """
#         #####################################
#         page_no = 1
#         ###################################################################################
        
#         def description_formatter(des: str) -> str:
#             # Split the description into words
#             words = des.split()
            
#             # Initialize variables
#             line = ""
#             formatted_description = []
            
#             for word in words:
#                 # Check if adding the next word would exceed the 32 character limit
#                 if len(line) + len(word) + 1 <= 32:
#                     # Add the word to the current line
#                     if line:
#                         line += " " + word  # Add space before the word if it's not the first word
#                     else:
#                         line = word
#                 else:
#                     # If the line exceeds 32 characters, add it to the formatted list and start a new line
#                     formatted_description.append(line)
#                     line = word  # Start the new line with the current word
            
#             # Add the last line to the formatted description
#             if line:
#                 formatted_description.append(line)
            
#             # Join the lines with newline characters
#             return "\n".join(formatted_description)
#         ###################################################################################
#         # set title
#         c.setTitle("Invoice")
        
#         # from ark_main import settingsD:\cod\zoro\ark_billing\ark_main 2\billing\static\asset\images\ARK_logo-01.png
#         logo_path = os.path.join(os.path.dirname(__file__), r"static/asset/images/ARK_logo-01.png")
#         # logo_path = os.path.join(settings.BASE_DIR, "ARK_logo-01.png")
        
#         # img bg
#         def draw_bg():
#             c.setFillAlpha(0.15)
#             c.drawImage(logo_path, x=65, y=220, height=350, width=450, mask="auto")
#             c.setFillAlpha(1)
        
#         # img margin top
#         # c.drawImage(r"c:\Users\SUPER-POTATO\Desktop\Picture11.png", x=0, y=height - margin_page_y)
        
#         def draw_navbar():
#             # img logo
#             c.drawImage(logo_path, x=0, y=715, width=207, height=130)
            
#             # address page top
#             c.setFont(font_family_bold, font_large)
#             c.setFillColor(colors.orange)
#             c.drawString( 200, 800, address_head)
#             c.setFillColor(colors.black) 
            
#             c.setFont(font_family, font_large)
#             temp_spacing = 800 
#             for line in address_body.splitlines():
#                 c.drawString(200, temp_spacing:= temp_spacing - line_spacing , line.strip())
            
#             temp_spacing = 800 
#             for line in contact_details.splitlines():
#                 c.drawRightString(width - 35, temp_spacing:= temp_spacing - line_spacing , line.strip())

#         draw_bg()
#         draw_navbar()

#         # shipping addresses
#         temp_spacing = 700
#         for i, line in enumerate(shipped_from_address.splitlines()):
#             if i == 1:
#                 c.setFont(font_family_bold, font_medium)
#                 c.drawString(margin_page_x, temp_spacing:= temp_spacing - line_spacing , line.strip())
#             else:
#                 c.setFont(font_family, font_medium)
#                 c.drawString(margin_page_x, temp_spacing:= temp_spacing - line_spacing , line.strip())
        
#         temp_spacing = 700
#         for i, line in enumerate(billed_to_address.splitlines()):
#             if i == 1:
#                 c.setFont(font_family_bold, font_medium)
#                 c.drawString(margin_page_x + 200, temp_spacing:= temp_spacing - line_spacing , line.strip())
#             else:
#                 c.setFont(font_family, font_medium)
#                 c.drawString(margin_page_x + 200, temp_spacing:= temp_spacing - line_spacing , line.strip())
        
        
#         # invoice heading
#         temp_spacing = 700
#         for i, line in enumerate(invoice_heading.splitlines()):
#             if i == 1:
#                 c.setFont(font_family_bold, font_extra_large)
#                 c.setFillColor(colors.orange)
#                 c.drawRightString(width-35, temp_spacing:= temp_spacing - line_spacing -5 , line.strip())
#                 c.setFillColor(colors.black)
#             else:
#                 c.setFont(font_family, font_medium)
#                 c.drawRightString(width-35, temp_spacing:= temp_spacing - line_spacing , line.strip())
        

#         # Table
#         invoice_data = [
#             # table head
#             ["Sn\nNo.", "Product Name", "HSNC", "MRP", "Rate", "Disc.", "Qnt", "CGST", "SGST", "IGST", "Total"],
#             # table body
#             ["1", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             ["2", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["3", description_formatter("Adwell Printers Static "), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["4", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["5", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["6", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["7", description_formatter("Adwell Printers Static Website"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["8", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["9", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["10", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["11", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["12", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["13", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["14", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["15", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["16", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["17", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["18", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["19", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["20", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["21", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["22", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["23", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["24", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["25", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["26", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["27", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["28", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["29", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#             # ["30", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "100","1,525.50","1,525.50","1,525.50", "10,000.00"],
#         ]
        
#         # 00 10 20 30 40 50 60 70 80 90 100
#         # 01 11 21 31 41 51 61 71 81 91 101
        
#         # .. .. .. .. .. .. -2-2 -1-2
#         # .. .. .. .. .. .. -2-1 -1-1
        
#         # create table
#         table = Table(invoice_data, colWidths=[20, 145, 35, 45, 40, 40, 35, 40, 40, 40 ,45])
        
#         # Add styles to the table
#         style = TableStyle([
#             ('GRID', (0, 0), (-1, -1), table_border, colors.black),
#             # alignments
#             ('VALIGN', (0, 2), (-1, -5), 'TOP'),   
#             ('ALIGN', (2, 2), (-1, -5), 'CENTER'),   
#             ('ALIGN', (2, 2), (-1, -5), 'CENTER'),   
#             ('BOTTOMPADDING', (0, 0), (-1, 0), 10),  
#             # font
#             ('FONTNAME', (0, 0), (-1, 0), font_family_bold),  
#             ('FONTNAME', (2, 2), (-1, -1), font_family),  
#             ('FONTSIZE', (0, 0), (-1, -1), font_small),   
#             # border
#             ('ROUNDEDCORNERS', table_corner),
#         ])

#         table.setStyle(style)
#         table_width, table_height = table.wrapOn(c, width, height)

#         ################################

#         # Page and layout configurations
#         page_height = 505
#         max_table_height_per_page = 345
#         initial_y_position = 500

#         # Calculate the number of rows per page
#         rows_per_page = 10 
#         total_rows = len(invoice_data)
#         page_no = ceil(total_rows / rows_per_page)
#         print("page_no: ", page_no)

#         # Draw the table across pages
#         current_row = 0

#         if page_no > 2:
#             for p in range(page_no):
#                 draw_bg()
#                 draw_navbar()

#                 # Get the data slice for the current page
#                 page_data = invoice_data[current_row:current_row + rows_per_page]
#                 current_row += rows_per_page

#                 # Create a new table for this page
#                 table = Table(page_data, colWidths=[20, 145, 35, 45, 40, 40, 35, 40, 40, 40, 45])
#                 table.setStyle(style)

#                 # Recalculate table height for each page
#                 table_width, table_height = table.wrapOn(c, width, height)

#                 # Draw the table on the canvas
#                 if p == 0:
#                     y_position = initial_y_position - table_height + 91
#                 else:
#                     y_position = initial_y_position - table_height + 191
#                 table.drawOn(c, margin_page_x, y_position)

#                 c.showPage()  # Start a new page for the next part of the table
            
#             draw_bg()
#             draw_navbar()


#         # page size setup
#         # if table_height > 345:     
#         #     # for single page 345, max size for a page 505 
#         #     page_no = 2
        
#         # else:
#         #     table.drawOn(c, margin_page_x, 500 - table_height + 91)

#         # if page_no > 2:
#         #     page_no = ceil(table_height / 505)
        
#         # # Draw the table on the canvas
#         # for p in range(page_no):
#         #     table.drawOn(c, margin_page_x, 500 - table_height + 91)
#         #     c.showPage()

#         if page_no == 1:
#             # table = Table(invoice_data, colWidths=[20, 145, 35, 45, 40, 40, 35, 40, 40, 40, 45])
#             table.drawOn(c, margin_page_x, 500 - table_height + 91)


#         print("table_height: ", table_height)

#         # GST SUMMARY
#         c.setFont(font_family, font_medium)
#         gst_summary = [
#             # table head
#             ["GST Summary", "", "Discount: 22,123456", "", "", ""],
#             # table body
#             ["No fo Qnt:", "1000", "ni total:", "1000", "Bill Discount", "100000"],
#             ["GST 1", "GST 2", "CGST", "1000", "Grand Total", "2000"],
#             ["16%", "16%", "SGST", "1000", "Total paid", "2000"],
#             ["1000000", "1000000", "Total", "100000", "Balance", "0"],
#         ]
        
#         # GST summary table
#         gst_table = Table(gst_summary, colWidths=[87.5, 87.5, 87.5 ,87.5 ,87.5 ,87.5])
#         gst_style = TableStyle([
#             # Table SPAN
#             ('SPAN', (0,0), (1,0)), ('SPAN', (2,0),(5,0)),
#             # Alignments
#             ('ALIGN', (0,0), (1,0), 'CENTER'), ('ALIGN', (2,0),(5,0), 'CENTER'),
#             ('ALIGN', (0,1), (0,1), 'LEFT'),
#             ('ALIGN', (1,1), (1,1), 'RIGHT'),
#             ('ALIGN', (0,2), (1,4), 'CENTER'),
#             ('ALIGN', (2,1), (3,4), 'LEFT'),
#             ('ALIGN', (4,1), (4,4), 'LEFT'),
#             ('ALIGN', (3,1), (3,4), 'RIGHT'),
#             ('ALIGN', (5,1), (5,4), 'RIGHT'),
#             # box
#             ('BOX', (0,0), (-1,-1), table_border, colors.black),
#             ('BOX', (0,0), (5,0), table_border, colors.black),
#             ('BOX', (0,0), (1,4), table_border, colors.black),
#             ('BOX', (2,0), (5,4), table_border, colors.black),
#             ('BOX', (2,1), (3,4), table_border, colors.black),
#             ('BOX', (0,1), (1,1), table_border, colors.black),
#             # font
#             ('FONT', (0,0), (5,0), font_family_bold, font_medium),
#             ('FONT', (1,1), (1,1), font_family_bold, font_medium),
#             ('FONT', (1,1), (1,1), font_family_bold, font_medium),
#             ('FONT', (5,1), (5,4), font_family_bold, font_medium),
#             # rouncorners
#             ('ROUNDEDCORNERS', table_corner),
#         ])
#         gst_table.setStyle(gst_style)
        
#         # Draw gst table
#         gst_table.wrapOn(c, width, 0)
#         gst_table.drawOn(c, margin_page_x, 140)

        
#         # Bank details
#         temp_spacing = 120
#         c.setFont(font_family, font_medium)
#         for i, line in enumerate(bank_details.splitlines()):
#             c.drawString( margin_page_x, temp_spacing:= temp_spacing - line_spacing , line.strip())
        
#         # Authorized signatory
#         c.setFont(font_family_bold, font_medium)
#         c.drawRightString(width - 35, temp_spacing:= temp_spacing + line_spacing, "Authorized Signatory")


#         ######################################################################

#         # finishing canvas
#         c.showPage()
#         c.save()
#         return response


class ReportBillManagementView(LoginRequiredMixin, ListView):
    model = BillModel
    template_name = "reports/report_list.html"
    context_object_name = "reports"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("customer")

        # Get filter values
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        invoice_no = self.request.GET.get("invoice_no", "").strip()
        customer_name = self.request.GET.get("customer_name", "").strip()

        # Convert dates if provided
        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)

        # Filter by invoice date range
        if start_date and end_date:
            queryset = queryset.filter(invoice_date__range=(start_date, end_date))
        elif start_date:
            queryset = queryset.filter(invoice_date__gte=start_date)
        elif end_date:
            queryset = queryset.filter(invoice_date__lte=end_date)

        # Filter by invoice number
        if invoice_no:
            queryset = queryset.filter(invoice_no__icontains=invoice_no)

        # Filter by customer name
        if customer_name:
            customer_ids = CustomerModel.objects.filter(
                customer_name__icontains=customer_name
            ).values_list("id", flat=True)
            queryset = queryset.filter(customer_id__in=customer_ids)

        # Total amount calculation
        self.total_amount = queryset.aggregate(total=Sum("total_amount"))["total"] or 0

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["start_date"] = self.request.GET.get("start_date", "")
        context["end_date"] = self.request.GET.get("end_date", "")
        context["invoice_no"] = self.request.GET.get("invoice_no", "")
        context["customer_name"] = self.request.GET.get("customer_name", "")
        context["total_amount"] = self.total_amount
        return context

# class ReportStockManagementView(LoginRequiredMixin, ListView):    # 5 Done
#     """Filter report based on date, product, and HSN."""
#     model = PurchaseStockProductModel
#     template_name = "reports/report_stock.html"
#     context_object_name = "reports"
#     paginate_by = 20
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#
#         # Get filter params
#         start_date = self.request.GET.get("start_date")
#         end_date = self.request.GET.get("end_date")
#         product_name = self.request.GET.get("product_name")
#         hsn_code = self.request.GET.get("hsn")
#
#         # Convert dates
#         if start_date:
#             start_date = parse_date(start_date)
#         if end_date:
#             end_date = parse_date(end_date)
#
#         # Apply filters only if provided
#         if start_date and end_date:
#             queryset = queryset.filter(created_at__date__range=(start_date, end_date))
#         elif start_date:
#             queryset = queryset.filter(created_at__date__gte=start_date)
#         elif end_date:
#             queryset = queryset.filter(created_at__date__lte=end_date)
#
#         if product_name:
#             queryset = queryset.filter(product__product_name__icontains=product_name.strip())
#
#         if hsn_code:
#             queryset = queryset.filter(hsn__icontains=hsn_code)
#
#         return queryset
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["start_date"] = self.request.GET.get("start_date", "")
#         context["end_date"] = self.request.GET.get("end_date", "")
#         context["product_name"] = self.request.GET.get("product_name", "")
#         context["hsn"] = self.request.GET.get("hsn", "")
#
#         # Aggregate total
#         filtered_qs = self.get_queryset()
#         total_grand = filtered_qs.aggregate(total=Sum("grandTotal"))["total"] or 0
#         context["total_grand"] = total_grand
#
#         return context
from django.core.paginator import Paginator

class ReportStockManagementView(LoginRequiredMixin, ListView):
    """Filter report based on date, product, and HSN."""
    model = PurchaseStockProductModel
    template_name = "reports/report_stock.html"
    context_object_name = "reports"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get filter params
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        product_name = self.request.GET.get("product_name")
        hsn_code = self.request.GET.get("hsn")

        # Convert dates
        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)

        # Apply filters
        if start_date and end_date:
            queryset = queryset.filter(created_at__date__range=(start_date, end_date))
        elif start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        elif end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        if product_name:
            queryset = queryset.filter(product__product_name__icontains=product_name.strip())

        if hsn_code:
            queryset = queryset.filter(hsn__icontains=hsn_code)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Keep form values in context
        context["start_date"] = self.request.GET.get("start_date", "")
        context["end_date"] = self.request.GET.get("end_date", "")
        context["product_name"] = self.request.GET.get("product_name", "")
        context["hsn"] = self.request.GET.get("hsn", "")

        # Pagination logic with annotation of total_units
        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        # Add start_index to use in template pagination
        start_index = page_obj.start_index()

        for i, product in enumerate(page_obj, start=start_index):
            product.total_units = (product.units or 0) + (product.discount_unit or 0)
            product.serial_number = i  # Optional: use this instead of counter in template

        context["reports"] = page_obj
        context["total_grand"] = queryset.aggregate(total=Sum("grandTotal"))["total"] or 0

        return context
class ReportStockBillManagementView(LoginRequiredMixin, ListView):    #3 done
    model = PurchaseStockModel
    template_name = "reports/report_stock_bill.html"
    context_object_name = "reports"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get filter parameters from GET
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        purchase_bill_id = self.request.GET.get("purchase_bill_id")
        supplier_name = self.request.GET.get("supplier_name")

        # Convert to date objects
        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)

        # Filter by date
        if start_date and end_date:
            queryset = queryset.filter(created_at__date__range=[start_date, end_date])
        elif start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        elif end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        # Filter by invoice number
        if purchase_bill_id:
            queryset = queryset.filter(purchase_bill_id__icontains=purchase_bill_id.strip())

        # Filter by supplier name (related field)
        if supplier_name:
            queryset = queryset.filter(supplier__supplier_name__icontains=supplier_name.strip())

        # Save total amount to use in context
        self.total_grand = queryset.aggregate(total=Sum("total_amount"))["total"] or 0
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["start_date"] = self.request.GET.get("start_date", "")
        context["end_date"] = self.request.GET.get("end_date", "")
        context["purchase_bill_id"] = self.request.GET.get("purchase_bill_id", "")
        context["supplier_name"] = self.request.GET.get("supplier_name", "")
        context["total_grand"] = self.total_grand
        return context


class SalesreportBillManagementView(LoginRequiredMixin, ListView):   # 6 Done
    model = PurchaseStockModel
    template_name = "reports/sales_report.html"
    context_object_name = "reports"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related("supplier")

        # Get parameters
        start_date = self.request.GET.get("start_date", "").strip()
        end_date = self.request.GET.get("end_date", "").strip()
        bill_id = self.request.GET.get("purchase_bill_id", "").strip()
        supplier_name = self.request.GET.get("supplier_name", "").strip()

        # Apply filters
        if start_date:
            parsed_start = parse_date(start_date)
            if parsed_start:
                queryset = queryset.filter(created_at__date__gte=parsed_start)

        if end_date:
            parsed_end = parse_date(end_date)
            if parsed_end:
                queryset = queryset.filter(created_at__date__lte=parsed_end)

        if bill_id.isdigit():
            queryset = queryset.filter(purchase_bill_id=int(bill_id))

        if supplier_name:
            supplier_ids = SupplierModel.objects.filter(
                supplier_name__icontains=supplier_name
            ).values_list("id", flat=True)
            queryset = queryset.filter(supplier_id__in=supplier_ids)

        # Store queryset for context and reuse
        self.filtered_queryset = queryset

        # Calculate total amount
        self.total_amount = queryset.aggregate(total=Sum("total_amount"))["total"] or 0

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["start_date"] = self.request.GET.get("start_date", "")
        context["end_date"] = self.request.GET.get("end_date", "")
        context["purchase_bill_id"] = self.request.GET.get("purchase_bill_id", "")
        context["supplier_name"] = self.request.GET.get("supplier_name", "")
        context["total_amount"] = self.total_amount
        return context
    

class PurchaseReportView(LoginRequiredMixin, ListView):   #1 done
    model = PurchaseStockModel
    template_name = "reports/purchase_report.html"
    context_object_name = "reports"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get filter parameters from GET
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        purchase_bill_id = self.request.GET.get("purchase_bill_id")
        supplier_name = self.request.GET.get("supplier_name")

        # Convert provided date strings to date objects
        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)

        # Filter by date range if provided
        if start_date and end_date:
            queryset = queryset.filter(created_at__date__range=[start_date, end_date])
        elif start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        elif end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        # Filter by invoice number if provided
        if purchase_bill_id:
            queryset = queryset.filter(purchase_bill_id__icontains=purchase_bill_id.strip())

        # ✅ Correct filtering through foreign key
        if supplier_name:
            queryset = queryset.filter(supplier__supplier_name__icontains=supplier_name.strip())

        # Aggregate total amount
        self.total_grand = queryset.aggregate(total=Sum('total_amount'))['total'] or 0

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass filter values back to template for input persistence
        context["start_date"] = self.request.GET.get("start_date", "")
        context["end_date"] = self.request.GET.get("end_date", "")
        context["purchase_bill_id"] = self.request.GET.get("purchase_bill_id", "")
        context["supplier_name"] = self.request.GET.get("supplier_name", "")
        context["total_grand"] = self.total_grand
        return context
    
class ReportStockManufactureManagementView(LoginRequiredMixin, ListView):    #4 done
    model = PurchaseStockModel
    template_name = "reports/report_stock_manufacture.html"
    context_object_name = "reports"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get filter parameters from GET
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        purchase_bill_id = self.request.GET.get("purchase_bill_id")
        supplier_name = self.request.GET.get("supplier_name")

        # Convert to date objects
        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)

        # Filter by date
        if start_date and end_date:
            queryset = queryset.filter(created_at__date__range=[start_date, end_date])
        elif start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        elif end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        # Filter by invoice number
        if purchase_bill_id:
            queryset = queryset.filter(purchase_bill_id__icontains=purchase_bill_id.strip())

        # Filter by supplier name (related field)
        if supplier_name:
            queryset = queryset.filter(supplier__supplier_name__icontains=supplier_name.strip())

        # Save total amount to use in context
        self.total_grand = queryset.aggregate(total=Sum("total_amount"))["total"] or 0
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["start_date"] = self.request.GET.get("start_date", "")
        context["end_date"] = self.request.GET.get("end_date", "")
        context["purchase_bill_id"] = self.request.GET.get("purchase_bill_id", "")
        context["supplier_name"] = self.request.GET.get("supplier_name", "")
        context["total_grand"] = self.total_grand
        return context  
    
class StockReportView(LoginRequiredMixin, ListView):   # done 8
    model = ProductModel
    template_name = "reports/stack_startment.html"
    context_object_name = "pro"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get filters from query params
        product_name = self.request.GET.get("product_name", "").strip()
        start_date = self.request.GET.get("start_date", "").strip()
        end_date = self.request.GET.get("end_date", "").strip()

        if product_name:
            queryset = queryset.filter(product_name__icontains=product_name)

        # Parse date filters
        start_date = parse_date(start_date) if start_date else None
        end_date = parse_date(end_date) if end_date else None

        # Apply custom annotations for each product instance
        for product in queryset:
            purchase_qs = PurchaseStockProductModel.objects.filter(product=product)
            bill_qs = BillProductModel.objects.filter(pro=product)

            if start_date:
                purchase_qs = purchase_qs.filter(created_at__date__gte=start_date)
                bill_qs = bill_qs.filter(bill__created_at__date__gte=start_date)
            if end_date:
                purchase_qs = purchase_qs.filter(created_at__date__lte=end_date)
                bill_qs = bill_qs.filter(bill__created_at__date__lte=end_date)

            product.stock_in_val = purchase_qs.aggregate(total=Sum('total_quantity'))['total'] or 0
            product.stock_out_val = bill_qs.aggregate(total=Sum('units'))['total'] or 0
            product.current_stock_val = product.stock_in_val - product.stock_out_val

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_name"] = self.request.GET.get("product_name", "")
        context["start_date"] = self.request.GET.get("start_date", "")
        context["end_date"] = self.request.GET.get("end_date", "")
        return context
    

# class MarginReportView(LoginRequiredMixin, ListView):    # done 1
#     model = BillProductModel
#     template_name = "reports/margin_report.html"
#     context_object_name = "margins"
#     paginate_by = 20
#
#     def get_queryset(self):
#         queryset = super().get_queryset().select_related('bill__customer')
#
#         # Get filters
#         product_name = self.request.GET.get("product_name", "").strip()
#         customer = self.request.GET.get("customer", "").strip()
#         start_date = self.request.GET.get("start_date", "").strip()
#         end_date = self.request.GET.get("end_date", "").strip()
#
#         # Convert dates
#         if start_date:
#             start_date = parse_date(start_date)
#         if end_date:
#             end_date = parse_date(end_date)
#
#         # Filter by date range
#         if start_date and end_date:
#             queryset = queryset.filter(bill__created_at__range=[start_date, end_date])
#         elif start_date:
#             queryset = queryset.filter(bill__created_at__gte=start_date)
#         elif end_date:
#             queryset = queryset.filter(bill__created_at__lte=end_date)
#
#         # Filter by product name (local field)
#         if product_name:
#             queryset = queryset.filter(product_name__icontains=product_name)
#
#         # Filter by customer name (from related model)
#         if customer:
#            queryset = queryset.filter(bill__customer__customer_name__icontains=customer.strip())
#
#         # Annotate profit/margin
#         purchase_price = Coalesce(F('product__buy_price'), Value(0))
#
#         queryset = queryset.annotate(
#             purchase_price=purchase_price,
#             profit_per_unit=ExpressionWrapper(
#                 F('sales_price') - purchase_price,
#                 output_field=FloatField()
#             ),
#             total_profit=ExpressionWrapper(
#                 (F('sales_price') - purchase_price) * F('units'),
#                 output_field=FloatField()
#             ),
#             margin_percentage=ExpressionWrapper(
#                 Case(
#                     When(product__buy_price__isnull=True, then=Value(0)),
#                     When(product__buy_price=0, then=Value(0)),
#                     default=((F('sales_price') - F('product__buy_price')) * 100) / F('product__buy_price'),
#                 ),
#                 output_field=FloatField()
#             )
#         ).order_by('-id')
#
#         # Total profit sum
#         self.total_profit = queryset.aggregate(total=Sum('total_profit'))['total'] or 0
#
#         return queryset
    from django.db.models import F, Value, FloatField, ExpressionWrapper, Sum, Case, When
    from django.db.models.functions import Coalesce
    from django.utils.dateparse import parse_date

class MarginReportView(LoginRequiredMixin, ListView):
        model = BillProductModel
        template_name = "reports/margin_report.html"
        context_object_name = "margins"
        paginate_by = 20

        def get_queryset(self):
            queryset = super().get_queryset().select_related(
                'bill__customer',
                'product__product',
                'product__purchase_stock',
                'product__purchase_stock__supplier'
            )

            product_name = self.request.GET.get("product_name", "").strip()
            customer = self.request.GET.get("customer", "").strip()
            start_date = self.request.GET.get("start_date", "").strip()
            end_date = self.request.GET.get("end_date", "").strip()

            if start_date:
                start_date = parse_date(start_date)
            if end_date:
                end_date = parse_date(end_date)

            if start_date and end_date:
                queryset = queryset.filter(bill__created_at__range=[start_date, end_date])
            elif start_date:
                queryset = queryset.filter(bill__created_at__gte=start_date)
            elif end_date:
                queryset = queryset.filter(bill__created_at__lte=end_date)

            if product_name:
                queryset = queryset.filter(product_name__icontains=product_name)
            if customer:
                queryset = queryset.filter(bill__customer__customer_name__icontains=customer)

            # Purchase price from related model
            purchase_price = Coalesce(F('product__buy_price'), Value(0))

            queryset = queryset.annotate(
                purchase_price=purchase_price,
                profit_per_unit=ExpressionWrapper(
                    F('sales_price') - purchase_price,
                    output_field=FloatField()
                ),
                total_profit=ExpressionWrapper(
                    (F('sales_price') - purchase_price) * F('units'),
                    output_field=FloatField()
                ),
                margin_percentage=ExpressionWrapper(
                    Case(
                        When(product__buy_price__isnull=True, then=Value(0)),
                        When(product__buy_price=0, then=Value(0)),
                        default=((F('sales_price') - F('product__buy_price')) * 100) / F('product__buy_price'),
                    ),
                    output_field=FloatField()
                )
            ).order_by('-id')

            self.total_profit = queryset.aggregate(total=Sum('total_profit'))['total'] or 0

            return queryset

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context.update({
                "product_name": self.request.GET.get("product_name", ""),
                "customer": self.request.GET.get("customer", ""),
                "start_date": self.request.GET.get("start_date", ""),
                "end_date": self.request.GET.get("end_date", ""),
                "total_profit": self.total_profit,
            })
            return context



      
class EstimationBillView(LoginRequiredMixin, ListView):
    template_name = "estimation/estimationview.html"
    model = BillModel
    paginate_by = 20
    context_object_name = "bills"
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_estimation=True)

class EstimationDetailView(LoginRequiredMixin, DetailView):
    template_name = "estimation/estimationdetail.html"
    model = BillModel
    context_object_name = "detail"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = BillProductModel.objects.filter(bill=self.get_object())
        return context

class EstimationToBillView(LoginRequiredMixin, UpdateView):
    model = BillModel
    fields = ["total_paid", "balance"]
    success_url = reverse_lazy("billing:bill")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.is_estimation = False
        self.object.save()
        return redirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        bill = get_object_or_404(BillModel, pk=kwargs['pk'])
        total_paid = request.POST.get("total_paid", "0")
        balance = request.POST.get("balance", "0")

        if total_paid and balance:
            bill.total_paid = total_paid
            bill.balance = balance
            bill.is_estimation = False
            bill.save()

        return redirect(self.success_url)