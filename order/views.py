from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.views import View
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from cart.cart import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm
from .pdfcreator import renderPdf
from django.http import JsonResponse, Http404
from django.urls import reverse
from django.core.exceptions import ValidationError
import json
import logging
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.template.loader import get_template
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import io
import traceback

logger = logging.getLogger(__name__)

@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def order_create(request):
	cart = Cart(request)
	if not request.user.is_authenticated:
		return redirect('store:signin')
	
	if len(cart) == 0:
		return redirect('store:books')

	customer = get_object_or_404(User, id=request.user.id)
	form = OrderCreateForm(request.POST or None, initial={
		"name": customer.first_name, 
		"email": customer.email
	})
	
	if request.method == 'POST':
		# Debug logging
		print("POST data:", request.POST)
		print("Form data:", form.data)
		print("Form is valid:", form.is_valid())
		
		if form.is_valid():
			try:
				# Get payment details
				payment_id = request.POST.get('payment_id')
				payment_status = request.POST.get('payment_status', 'COMPLETED')
				
				if not payment_id:
					return JsonResponse({
						'success': False,
						'error': 'Payment information is missing'
					})

				# Create order
				order = form.save(commit=False)
				order.customer = request.user
				order.payable = cart.get_total_price()
				order.totalbook = len(cart)
				order.paid = True
				order.payment_method = 'PayPal'
				order.payment_id = payment_id
				order.payment_status = payment_status
				order.save()

				# Create order items
				for item in cart:
					OrderItem.objects.create(
						order=order,
						book=item['book'],
						price=item['price'],
						quantity=item['quantity']
					)

				# Clear the cart
				cart.clear()

				return JsonResponse({
					'success': True,
					'redirect_url': reverse('order:order_success', kwargs={'order_id': order.id})
				})

			except Exception as e:
				logger.error(f"Order creation error: {str(e)}")
				return JsonResponse({
					'success': False,
					'error': str(e)
				})
		else:
			# Convert form errors to dict
			field_errors = {}
			for field, errors in form.errors.items():
				field_errors[field] = str(errors[0])  # Get first error message
			
			return JsonResponse({
				'success': False,
				'error': 'Please fill in all required fields',
				'field_errors': field_errors
			})

	return render(request, 'order/order.html', {
		"form": form,
		"cart": cart,
		"cost": cart.get_total_price()
	})

def order_list(request):
	my_order = Order.objects.filter(customer_id = request.user.id).order_by('-created')
	paginator = Paginator(my_order, 5)
	page = request.GET.get('page')
	myorder = paginator.get_page(page)

	return render(request, 'order/list.html', {"myorder": myorder})

def order_details(request, id):
	order_summary = get_object_or_404(Order, id=id)

	if order_summary.customer_id != request.user.id:
		return redirect('store:index')

	orderedItem = OrderItem.objects.filter(order_id=id)
	context = {
		"o_summary": order_summary,
		"o_item": orderedItem
	}
	return render(request, 'order/details.html', context)

class pdf(View):
    def get(self, request, id):
        try:
            order = get_object_or_404(Order, id=id)
            
            # Check if the user has permission to access this order
            if order.customer_id != request.user.id:
                raise Http404("Order not found")
            
            # Get order items
            order_items = OrderItem.objects.filter(order=order)
            
            # Prepare context for PDF
            context = {
                "order": order,
                "order_items": order_items,
                "total": order.payable,
                "shipping": 100,  # Adjust based on your shipping calculation
                "subtotal": order.payable - 100  # Adjust based on your calculation
            }
            
            # Generate PDF
            template = get_template('order/pdf.html')
            pdf = renderPdf('order/pdf.html', context)
            
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = f"Invoice_{order.id}.pdf"
                content = f"inline; filename={filename}"
                response['Content-Disposition'] = content
                return response
            
            return HttpResponse("Error Rendering PDF", status=400)
            
        except Exception as e:
            print(f"PDF generation error: {str(e)}")
            return HttpResponse("Error generating PDF", status=500)

def order_success(request, order_id):
	order = get_object_or_404(Order, id=order_id)
	if order.customer_id != request.user.id:
		return redirect('store:index')
	return render(request, 'order/successfull.html', {'order': order})

def generate_pdf(request, order_id):
    try:
        # Get the order and verify permissions
        order = get_object_or_404(Order, id=order_id)
        if order.customer_id != request.user.id:
            raise Http404("Order not found")
        
        logger.info(f"Starting PDF generation for order {order_id}")
        
        # Create a file-like buffer to receive PDF data
        buffer = io.BytesIO()
        
        try:
            # Create the PDF object, using the buffer as its "file."
            p = canvas.Canvas(buffer, pagesize=letter)
            
            # Draw things on the PDF
            # Header
            p.setFont("Helvetica", 16)  # Using regular Helvetica for header
            p.drawString(50, 750, f"Order Invoice #{order.id}")
            
            # Customer Information
            p.setFont("Helvetica", 12)
            p.drawString(50, 700, f"Customer Name: {order.name}")
            p.drawString(50, 680, f"Email: {order.email}")
            p.drawString(50, 660, f"Phone: {order.phone}")
            p.drawString(50, 640, f"Address: {order.address}")
            p.drawString(50, 620, f"{order.district}, {order.division} - {order.zip_code}")
            
            # Order Details
            p.setFont("Helvetica", 14)  # Using regular Helvetica
            p.drawString(50, 580, "Order Details")
            
            # Table header
            p.setFont("Helvetica", 12)
            p.drawString(50, 550, "Book")
            p.drawString(300, 550, "Quantity")
            p.drawString(400, 550, "Price")
            
            # Items
            y = 520
            order_items = OrderItem.objects.filter(order=order)
            logger.info(f"Found {order_items.count()} items for order {order_id}")
            
            for item in order_items:
                try:
                    book_name = str(item.book)
                    if len(book_name) > 30:
                        book_name = book_name[:27] + "..."
                    p.drawString(50, y, book_name)
                    p.drawString(300, y, str(item.quantity))
                    p.drawString(400, y, f"${item.price}")
                    y -= 20
                except Exception as item_error:
                    logger.error(f"Error processing item {item.id}: {str(item_error)}")
            
            # Payment Information
            p.setFont("Helvetica", 12)
            p.drawString(50, y-20, "Payment Information")
            p.drawString(50, y-40, f"Payment Method: {order.payment_method}")
            p.drawString(50, y-60, f"Payment Status: {'Paid' if order.paid else 'Pending'}")
            p.drawString(50, y-80, f"Total Amount: ${order.payable}")
            
            if order.transaction_id:
                p.drawString(50, y-100, f"Transaction ID: {order.transaction_id}")
            
            # Draw footer
            p.setFont("Helvetica", 8)
            p.drawString(50, 50, "Thank you for your purchase!")
            
            # Close the PDF object cleanly
            p.showPage()
            p.save()
            
            # FileResponse instead of HttpResponse for better file handling
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            filename = f"order_{order.id}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            logger.info(f"Successfully generated PDF for order {order_id}")
            return response
            
        except Exception as pdf_error:
            logger.error(f"PDF generation error: {str(pdf_error)}")
            logger.error(traceback.format_exc())
            raise  # Re-raise to be caught by outer try-except
            
    except Exception as e:
        logger.error(f"Order {order_id} PDF generation failed: {str(e)}")
        logger.error(traceback.format_exc())
        return HttpResponse(
            f"Error generating PDF. Please contact support. Error: {str(e)}", 
            status=500,
            content_type='text/plain'
        )
