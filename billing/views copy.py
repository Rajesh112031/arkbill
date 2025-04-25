from django.views.generic import TemplateView, CreateView, ListView, DeleteView, View
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.db.models import Q
from django.utils.timezone import now

from .models import *
from .forms import * 

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle   


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
    template_name = "Supplier/Supplier.html"
    model = SupplierModel
    fields = "__all__"
    paginate_by = 20
    context_object_name = "suppliers"

class SupplierEntryView(LoginRequiredMixin, CreateView):
    template_name = "Supplier/newSupplier.html"
    form_class = SupplierForm
    success_url = reverse_lazy("billing:supplier_list")
    
class PurchasedStockEntryView(LoginRequiredMixin, CreateView):
    template_name = "purchasestock/purchaseentry.html"
    form_class = PurchasedStockEntryForm
    success_url = reverse_lazy("billing:purchased_stock")
    
    def form_valid(self, form):
        bill_id = now().strftime("%Y%m%d%H%M%S")
        while PurchaseStockModel.objects.filter(purchase_bill_id=bill_id).exists():
            bill_id += str(int(bill_id) + 1)
        form.instance.purchase_bill_id = bill_id
        form.save()
        
        index = self.request.POST.get("indexValue", None)
        if index is None:
            return super().form_invalid(form)
        
        for i in range(1, int(index)+1):
            PurchaseStockProductModel.objects.create(purchase_stock = PurchaseStockModel.objects.get(purchase_bill_id = bill_id),
                                                        product = ProductModel.objects.get(id = int(self.request.POST.get(f"product_id_{i}"))),
                                                        hsn = self.request.POST.get(f"hsn_{i}"),
                                                        pack_size = self.request.POST.get(f"pack_size_{i}"),
                                                        mrp = self.request.POST.get(f"mrp_{i}"),
                                                        sales_price = self.request.POST.get(f"sales_price_{i}"),
                                                        units = self.request.POST.get(f"quantity_{i}"),
                                                        batch_no = self.request.POST.get(f"batch_{i}"),
                                                        discount_percentage_1 = self.request.POST.get(f"discount_percentage_{i}"),
                                                        discount_amount_1 = self.request.POST.get(f"discount_amount_{i}"),
                                                        discount_percentage_2 = self.request.POST.get(f"added_discount_{i}"),
                                                        discount_amount_2 = self.request.POST.get(f"added_discount_amount_{i}"),
                                                        discount_unit = self.request.POST.get(f"free_quantity_{i}"),
                                                        sgst_percentage = self.request.POST.get(f"sgst_{i}"),
                                                        sgst_amount = self.request.POST.get(f"sgst_amount_{i}"),
                                                        cgst_percentage = self.request.POST.get(f"cgst_{i}"),
                                                        cgst_amount = self.request.POST.get(f"cgst_amount_{i}"),
                                                        igst_percentage = self.request.POST.get(f"igst_{i}"),
                                                        igst_amount = self.request.POST.get(f"igst_amount_{i}"),
                                                        manufacturing = self.request.POST.get(f"manufacture_{i}"),
                                                        expiring = self.request.POST.get(f"expiring_{i}"),
                                                        total_quantity = self.request.POST.get(f"total_quantity_{i}"),
                                                        total_price = self.request.POST.get(f"total_price_{i}"),
                                                        totalTax = self.request.POST.get(f"totalTax_{i}"),
                                                        grandTotal = self.request.POST.get(f"grandTotal_{i}")
                                                    )
            
        return redirect(self.success_url)
    
class PurchasedStockView(LoginRequiredMixin, ListView):
    template_name = "purchasestock/purchased.html"
    model = PurchaseStockProductModel
    paginate_by = 20
    context_object_name = "products"
    
class SupplierSearchView(LoginRequiredMixin, ListView):
    model = SupplierModel
    context_object_name = "supplier"

    def get_queryset(self):
        query = self.request.GET.get("query", "")
        if query:
            return SupplierModel.objects.filter(
                Q(supplier_name__icontains=query) | Q(supplier_id__icontains=query)
            ).only("supplier_id",
                   "supplier_name",
                   "supplier_phone",
                   "supplier_state",
                   "supplier_account_balance")[:10]
        # print(ProductModel.objects.all()[:10])
        return SupplierModel.objects.all().only("supplier_id",
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
            ).only("product_name",
                   "id",
                   "product_code",
                   "product_hsn",
                   "product_barcode",
                   "product_packtype",
                   "pack_size")[:10]
        # print(ProductModel.objects.all()[:10])
        return ProductModel.objects.all().only("product_name",
                   "id",
                   "product_code",
                   "product_hsn",
                   "product_barcode",
                   "product_packtype",
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
    ...
    
class BillEntryView(LoginRequiredMixin, CreateView):
    template_name = "bill/billentry.html"
    form_class = BillEntryForm
    success_url = reverse_lazy("billing:bill")
    
    def form_valid(self, form):
        bill_id = now().strftime("%Y%m%d%H%M%S")
        while PurchaseStockModel.objects.filter(purchase_bill_id=bill_id).exists():
            bill_id += str(int(bill_id) + 1)
        form.instance.purchase_bill_id = bill_id
        form.save()
        
        index = self.request.POST.get("indexValue", None)
        if index is None:
            return super().form_invalid(form)
        
        for i in range(1, int(index)+1):
            PurchaseStockProductModel.objects.create(purchase_stock = PurchaseStockModel.objects.get(purchase_bill_id = bill_id),
                                                        product = ProductModel.objects.get(id = int(self.request.POST.get(f"product_id_{i}"))),
                                                        hsn = self.request.POST.get(f"hsn_{i}"),
                                                        pack_size = self.request.POST.get(f"pack_size_{i}"),
                                                        mrp = self.request.POST.get(f"mrp_{i}"),
                                                        sales_price = self.request.POST.get(f"sales_price_{i}"),
                                                        units = self.request.POST.get(f"quantity_{i}"),
                                                        batch_no = self.request.POST.get(f"batch_{i}"),
                                                        discount_percentage_1 = self.request.POST.get(f"discount_percentage_{i}"),
                                                        discount_amount_1 = self.request.POST.get(f"discount_amount_{i}"),
                                                        discount_percentage_2 = self.request.POST.get(f"added_discount_{i}"),
                                                        discount_amount_2 = self.request.POST.get(f"added_discount_amount_{i}"),
                                                        discount_unit = self.request.POST.get(f"free_quantity_{i}"),
                                                        sgst_percentage = self.request.POST.get(f"sgst_{i}"),
                                                        sgst_amount = self.request.POST.get(f"sgst_amount_{i}"),
                                                        cgst_percentage = self.request.POST.get(f"cgst_{i}"),
                                                        cgst_amount = self.request.POST.get(f"cgst_amount_{i}"),
                                                        igst_percentage = self.request.POST.get(f"igst_{i}"),
                                                        igst_amount = self.request.POST.get(f"igst_amount_{i}"),
                                                        manufacturing = self.request.POST.get(f"manufacture_{i}"),
                                                        expiring = self.request.POST.get(f"expiring_{i}"),
                                                        total_quantity = self.request.POST.get(f"total_quantity_{i}"),
                                                        total_price = self.request.POST.get(f"total_price_{i}"),
                                                        totalTax = self.request.POST.get(f"totalTax_{i}"),
                                                        grandTotal = self.request.POST.get(f"grandTotal_{i}")
                                                    )
            
        return redirect(self.success_url)

class PDFView(View):
    def get(self, request, *args, **kwargs):
        
        # create httpsresponse content type set to pdf
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = "inline; filename='invoice.pdf'"
        
        # create canvas
        c = canvas.Canvas(response, pagesize=A4)
        
        width, height = A4
        print("width: ", width, "height: ", height) 
        # width:  595.2755905511812 height:  841.8897637795277
        
        ######################################################################
        ####################           :)             ########################
        ######################################################################
        
        # root values
        width, height = 595, 841
        
        font_family = "Helvetica"
        font_family_bold = "Helvetica-Bold"
        font_medium = 10
        font_large = 13
        line_spacing = 15
        
        margin_page_x = 25
        margin_page_y = 20
        margin_page_x_text = 5
        
        margin_x = 60
        margin_y = 30
        
        y_span = 0
        
        
        # set title
        c.setTitle("Invoice")
        
        # img bg
        c.setFillAlpha(0.4)  # Set opacity to 50%
        c.drawImage(r"c:\Users\SUPER-POTATO\Desktop\ARK_logo-01.png", x=65, y=220, height=350, width=450, mask="auto")
        c.setFillAlpha(1)  # Set opacity to 50%
        
        # img margin top
        # c.drawImage(r"c:\Users\SUPER-POTATO\Desktop\Picture11.png", x=0, y=height - margin_page_y)
        
        # img logo
        c.drawImage(r"c:\Users\SUPER-POTATO\Desktop\ARK_logo-01.PNG", x=0, y=600, width=207, height=130)
        
        # address

        c.setFont(font_family_bold, font_medium)
        # receiver details
        receiver_name = "AJ"
        receiver_address = """81/4181, Ambili Towers,
Opp. Kgof Press Club Road,
Ootukuzhy Junction,
Statue Area, Trivandrum,
Kerala- 695 001."""
        
        receiver_details = f"""Name: {receiver_name}
Billing Address: 
{receiver_address}
    """
        
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
            
        # Sample data for the invoice
        invoice_data = [
            # table head
            ["Sn\nNo.", "Description of Services", "Qty", "Rate", "Actual\nAmt.", "IGST", "", "Total"],
            ["", "", "", "", "", "%", "Amt.", ""],
            # table body
            ["1", description_formatter("Adwell Printers Static Website + Domain name+ Shared Hosting + Standard SSL Certificate for 1 Year"), "1", "8,475.00", "8,475.00", "18", "1,525.50", "10,000.00"],
            # table footer
            ["Total", "", "", "", "", "10,000.00", "", ""],
            ["Total Amt. Before Tax:", "", "", "", "", "10,000.00", "", ""],
            ["GST:", "", "", "", "", "10,000.00", "", ""],
            ["Total Amt. Round Off.", "", "", "", "", "10,000.00", "", ""],
        ]
        
        # 00 10 20 30 40 50 60 70 
        # 01 11 21 31 41 51 61 71 
        
        # .. .. .. .. .. .. -2-2 -1-2
        # .. .. .. .. .. .. -2-1 -1-1
        
        # create table
        table = Table(invoice_data, colWidths=[30, 195, 25, 60, 60, 40, 65, 65])
        
        # Add styles to the table
        style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 1.5, colors.black),
            
            # table header
            ('SPAN', (0,0), (0,1)),
            ('SPAN', (1,0), (1,1)),
            ('SPAN', (2,0), (2,1)),
            ('SPAN', (3,0), (3,1)),
            ('SPAN', (4,0), (4,1)),
            ('SPAN', (7,0), (7,1)),
            ('SPAN', (5,0), (6,0)),
            
            # table footer -1
            ('SPAN', (-1,-1), (-3,-1)),
            ('SPAN', (-4,-1), (-8,-1)),
            
            # table footer -2
            ('SPAN', (-1,-2), (-3,-2)),
            ('SPAN', (-4,-2), (-8,-2)),
            
            # table footer -3
            ('SPAN', (-1,-3), (-3,-3)),
            ('SPAN', (-4,-3), (-8,-3)),
            
            # table footer -4
            ('SPAN', (-1,-4), (-3,-4)),
            ('SPAN', (-4,-4), (-8,-4)),
            
            # alignments
            ('VALIGN', (0, 2), (-1, -5), 'TOP'),   
            ('ALIGN', (2, 2), (-1, -5), 'CENTER'),   
            ('ALIGN', (2, 2), (-1, -5), 'CENTER'),   
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),  
            
            # ('ALIGN', (-1, -1), (-1, -3), 'LEFT'),   
            
            ('FONTNAME', (0, 0), (-1, 0), font_family_bold),  
            ('FONTNAME', (2, 2), (-1, -1), font_family),  
            ('FONTSIZE', (0, 0), (-1, -1), font_medium),   
            
        ])
        table.setStyle(style)
        
        table_width, table_height = table.wrapOn(c, width, height)
        x_position = margin_page_x
        y_position = y_span - table_height
        y_span -= table_height 

        # Draw the table on the canvas
        table.drawOn(c, x_position, y_position)

        ###################################################################################
        
        # bank details
        y_span -= 20
        bank_details = f"""Account Holder Name: """

        c.setFont(font_family_bold, font_medium)
        c.drawString(margin_page_x+margin_page_x_text, y_span:=y_span-line_spacing, "Our Bank Account Details")
        
        c.setFont(font_family, font_medium)
        for line in bank_details.splitlines():
            c.drawString(margin_page_x+margin_page_x_text, y_span:=y_span-line_spacing, line)
            
        # yspan right
        c.setFont(font_family_bold, font_medium)
        c.drawRightString(width-margin_page_x-margin_page_x_text, y_span, "For Clovion Tech Solutions Pvt. Ltd")
            
        # invoice status
        c.drawString(margin_page_x+margin_page_x_text, y_span:=y_span-line_spacing-margin_y, "Invoice Status: ")
        c.setFillColor(colors.green)
        c.drawString(margin_page_x+margin_page_x_text+90, y_span, "title")
        

        ######################################################################
        
        # finishing canvas
        c.showPage()
        c.save()
        
        return response
