import json
import logging
import threading
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import escape
from django.db import models
from .models import Hero, Benefit, Product, Order, OrderItem, FormulaSection, ContactMessage, Review, ReviewSectionSettings, BlogPost

logger = logging.getLogger(__name__)


def home(request):
    hero = Hero.objects.first()
    benefits = Benefit.objects.all()
    products = Product.objects.filter(is_available=True).order_by('price')
    product = products.first()
    formula = FormulaSection.objects.first()
    reviews = Review.objects.filter(is_approved=True).order_by('order', '-created_at')
    review_settings = ReviewSectionSettings.objects.first()
    blog_posts = BlogPost.objects.filter(is_published=True, is_featured=True)[:3]

    return render(request, "index.html", {
        "hero": hero,
        "benefits": benefits,
        "products": products,
        "product": product,
        "formula": formula,
        "reviews": reviews,
        "review_settings": review_settings,
        "blog_posts": blog_posts,
    })


def submit_review(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        rating = int(request.POST.get("rating", 5))
        comment = request.POST.get("comment", "").strip()
        city = request.POST.get("city", "").strip()

        if name and comment:
            Review.objects.create(
                name=name,
                rating=min(max(rating, 1), 5),
                comment=comment,
                city=city if city else None,
                verified_badge="Verified Customer",
                is_approved=True
            )
            messages.success(request, "Thank you! Your review has been submitted successfully.")
        else:
            messages.error(request, "Please enter your name and review message.")
    return redirect('home')



def checkout(request):
    product = Product.objects.filter(is_available=True).first()

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        city = request.POST.get("city")
        postal_code = request.POST.get("postal_code", "")
        payment_method = request.POST.get("payment_method", "cod")
        transaction_id = request.POST.get("transaction_id", "")
        cart_data_raw = request.POST.get("cart_data", "[]")

        try:
            cart_items = json.loads(cart_data_raw)
        except Exception:
            cart_items = []

        total_amount = 0
        if cart_items:
            for item in cart_items:
                price = float(item.get("price", product.price if product else 1499))
                qty = int(item.get("quantity", 1))
                total_amount += price * qty
        else:
            # Fallback if cart parameter was missing
            price = float(product.price) if product else 1499.0
            total_amount = price
            cart_items = [{
                "name": product.name if product else "Hair Growth Oil",
                "price": price,
                "quantity": 1
            }]

        order = Order.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            postal_code=postal_code,
            payment_method=payment_method,
            transaction_id=transaction_id,
            total_amount=total_amount,
            status='pending'
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product_name=item.get("name", "Product"),
                price=float(item.get("price", 1499)),
                quantity=int(item.get("quantity", 1))
            )

        # Send order notification email to admin
        send_order_notification(order, cart_items)

        return redirect('order_success', order_id=order.id)

    return render(request, "checkout.html", {
        "product": product
    })


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "order_success.html", {
        "order": order
    })


def send_order_notification(order, cart_items):
    """
    Sends a beautiful HTML email to admin whenever a new order is placed.
    Runs in a background thread so checkout redirect is instant.
    """
    admin_email = getattr(settings, 'ADMIN_EMAIL_RECIPIENT', 'khudashkhan489@gmail.com')
    from_email  = getattr(settings, 'DEFAULT_FROM_EMAIL', admin_email)

    payment_labels = {
        'easypaisa': 'Easypaisa',
        'jazzcash':  'JazzCash',
        'meezan':    'Meezan Bank',
        'hbl':       'HBL Bank',
        'cod':       'Cash on Delivery',
    }
    payment_display = payment_labels.get(order.payment_method, order.payment_method.upper())

    # Build items rows
    items_rows_html = ''
    items_plain     = ''
    for item in cart_items:
        name  = escape(str(item.get('name', 'Product')))
        qty   = item.get('quantity', 1)
        price = float(item.get('price', 0))
        subtotal = price * int(qty)
        items_rows_html += f"""
            <tr>
                <td style="padding:10px 12px;border-bottom:1px solid #f3f4f6;font-size:14px;color:#111827;">{name}</td>
                <td style="padding:10px 12px;border-bottom:1px solid #f3f4f6;font-size:14px;color:#374151;text-align:center;">{qty}</td>
                <td style="padding:10px 12px;border-bottom:1px solid #f3f4f6;font-size:14px;color:#374151;text-align:right;">Rs. {price:,.0f}</td>
                <td style="padding:10px 12px;border-bottom:1px solid #f3f4f6;font-size:14px;font-weight:700;color:#15803d;text-align:right;">Rs. {subtotal:,.0f}</td>
            </tr>"""
        items_plain += f"  - {name} x{qty} @ Rs.{price:.0f} = Rs.{subtotal:.0f}\n"

    plain_text = f"""Naya Order Aaya! 🛍️

Order ID : #HG-{order.id}
Customer : {order.full_name}
Email    : {order.email}
Phone    : {order.phone}
Address  : {order.address}
City     : {order.city}
Postal   : {order.postal_code or 'N/A'}
Payment  : {payment_display}
Txn ID   : {order.transaction_id or 'N/A'}
Status   : {order.status.upper()}

Items:
{items_plain}
Total Amount: Rs. {float(order.total_amount):,.0f}

Admin Panel: http://127.0.0.1:8000/admin/store/order/{order.id}/change/
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f0f4f1;margin:0;padding:20px;">
  <div style="max-width:620px;margin:0 auto;background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#10291d 0%,#15803d 100%);padding:28px 28px 24px;text-align:center;">
      <h1 style="margin:0;color:#fff;font-size:26px;font-weight:800;">Hair<span style="color:#d9a441;">Bloom</span></h1>
      <p style="margin:8px 0 0;color:#d1fae5;font-size:13px;">🎉 Naya Order Receive Hua!</p>
    </div>

    <!-- Order ID Banner -->
    <div style="background:#f0fdf4;border-bottom:2px solid #bbf7d0;padding:16px 28px;display:flex;align-items:center;justify-content:space-between;">
      <div>
        <p style="margin:0;font-size:12px;color:#6b7280;font-weight:600;text-transform:uppercase;letter-spacing:.06em;">Order ID</p>
        <p style="margin:4px 0 0;font-size:22px;font-weight:800;color:#15803d;">#HG-{order.id}</p>
      </div>
      <div style="text-align:right;">
        <p style="margin:0;font-size:12px;color:#6b7280;">Status</p>
        <span style="background:#fef9c3;color:#92400e;font-size:11px;font-weight:700;padding:4px 12px;border-radius:999px;text-transform:uppercase;">Pending</span>
      </div>
    </div>

    <div style="padding:24px 28px;">

      <!-- Customer Info -->
      <h2 style="margin:0 0 14px;font-size:15px;font-weight:700;color:#111827;border-bottom:2px solid #f3f4f6;padding-bottom:8px;">👤 Customer Details</h2>
      <table style="width:100%;border-collapse:collapse;margin-bottom:22px;">
        <tr>
          <td style="padding:8px 0;color:#6b7280;font-size:12px;font-weight:600;text-transform:uppercase;width:120px;">Full Name</td>
          <td style="padding:8px 0;font-size:14px;font-weight:700;color:#111827;">{escape(order.full_name)}</td>
        </tr>
        <tr>
          <td style="padding:8px 0;color:#6b7280;font-size:12px;font-weight:600;text-transform:uppercase;">Email</td>
          <td style="padding:8px 0;font-size:14px;"><a href="mailto:{escape(order.email)}" style="color:#15803d;font-weight:600;">{escape(order.email)}</a></td>
        </tr>
        <tr>
          <td style="padding:8px 0;color:#6b7280;font-size:12px;font-weight:600;text-transform:uppercase;">Phone</td>
          <td style="padding:8px 0;font-size:14px;font-weight:600;color:#111827;">{escape(order.phone)}</td>
        </tr>
        <tr>
          <td style="padding:8px 0;color:#6b7280;font-size:12px;font-weight:600;text-transform:uppercase;">Address</td>
          <td style="padding:8px 0;font-size:14px;color:#374151;">{escape(order.address)}</td>
        </tr>
        <tr>
          <td style="padding:8px 0;color:#6b7280;font-size:12px;font-weight:600;text-transform:uppercase;">City</td>
          <td style="padding:8px 0;font-size:14px;font-weight:600;color:#111827;">{escape(order.city)}</td>
        </tr>
        {f'<tr><td style="padding:8px 0;color:#6b7280;font-size:12px;font-weight:600;text-transform:uppercase;">Postal Code</td><td style="padding:8px 0;font-size:14px;color:#374151;">{escape(order.postal_code)}</td></tr>' if order.postal_code else ''}
      </table>

      <!-- Payment Info -->
      <h2 style="margin:0 0 14px;font-size:15px;font-weight:700;color:#111827;border-bottom:2px solid #f3f4f6;padding-bottom:8px;">💳 Payment Details</h2>
      <table style="width:100%;border-collapse:collapse;margin-bottom:22px;">
        <tr>
          <td style="padding:8px 0;color:#6b7280;font-size:12px;font-weight:600;text-transform:uppercase;width:120px;">Method</td>
          <td style="padding:8px 0;font-size:14px;font-weight:700;color:#111827;">{escape(payment_display)}</td>
        </tr>
        {f'<tr><td style="padding:8px 0;color:#6b7280;font-size:12px;font-weight:600;text-transform:uppercase;">Transaction ID</td><td style="padding:8px 0;font-size:14px;color:#374151;font-family:monospace;">{escape(order.transaction_id)}</td></tr>' if order.transaction_id else ''}
      </table>

      <!-- Order Items -->
      <h2 style="margin:0 0 14px;font-size:15px;font-weight:700;color:#111827;border-bottom:2px solid #f3f4f6;padding-bottom:8px;">🛍️ Order Items</h2>
      <table style="width:100%;border-collapse:collapse;margin-bottom:8px;">
        <thead>
          <tr style="background:#f9fafb;">
            <th style="padding:10px 12px;text-align:left;font-size:11px;color:#6b7280;font-weight:700;text-transform:uppercase;">Product</th>
            <th style="padding:10px 12px;text-align:center;font-size:11px;color:#6b7280;font-weight:700;text-transform:uppercase;">Qty</th>
            <th style="padding:10px 12px;text-align:right;font-size:11px;color:#6b7280;font-weight:700;text-transform:uppercase;">Price</th>
            <th style="padding:10px 12px;text-align:right;font-size:11px;color:#6b7280;font-weight:700;text-transform:uppercase;">Subtotal</th>
          </tr>
        </thead>
        <tbody>{items_rows_html}</tbody>
      </table>

      <!-- Total -->
      <div style="background:#f0fdf4;border:2px solid #bbf7d0;border-radius:14px;padding:16px 20px;display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;">
        <span style="font-size:15px;font-weight:700;color:#374151;">Total Amount</span>
        <span style="font-size:24px;font-weight:800;color:#15803d;">Rs. {float(order.total_amount):,.0f}</span>
      </div>

      <!-- CTA -->
      <div style="text-align:center;">
        <a href="http://127.0.0.1:8000/admin/store/order/{order.id}/change/"
           style="display:inline-block;background:#15803d;color:#fff;padding:13px 32px;border-radius:999px;text-decoration:none;font-weight:700;font-size:14px;">
          View Order in Admin Panel →
        </a>
      </div>

    </div>

    <!-- Footer -->
    <div style="background:#f9fafb;padding:14px 28px;text-align:center;font-size:12px;color:#9ca3af;border-top:1px solid #f3f4f6;">
      Yeh email automatically aapko bheja gaya jab Order #HG-{order.id} place hua.
    </div>
  </div>
</body>
</html>"""

    def _send():
        try:
            send_mail(
                subject=f"🛍️ Naya Order #HG-{order.id} - {order.full_name} - Rs. {float(order.total_amount):,.0f}",
                message=plain_text,
                from_email=from_email,
                recipient_list=[admin_email],
                html_message=html_content,
                fail_silently=False,
            )
            logger.info("Order notification email sent for Order #%s", order.id)
        except Exception as e:
            logger.error("Failed to send order notification: %s", e, exc_info=True)

    threading.Thread(target=_send, daemon=True).start()


def send_contact_notification(name, email, phone, subject, message):
    """
    Sends an email notification to the site administrator when a contact form is submitted.
    Runs asynchronously in a background thread so the user doesn't experience delay.
    """
    admin_email = getattr(settings, 'ADMIN_EMAIL_RECIPIENT', 'khudashkhan489@gmail.com')
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', admin_email)
    mail_subject = f"🔔 New Contact Message: {subject if subject else 'Website Inquiry'} - {name}"
    
    plain_text = f"""Assalam-o-Alaikum,

You have received a new contact message from your website:

--------------------------------------------------
Sender Details:
--------------------------------------------------
• Name: {name}
• Email: {email}
• Phone: {phone if phone else 'Not provided'}
• Subject: {subject if subject else 'General Inquiry'}

--------------------------------------------------
Message:
--------------------------------------------------
{message}

--------------------------------------------------
Reply directly to the sender at: {email}
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: 1px solid #e5e7eb;">
        <div style="background: linear-gradient(135deg, #10291d 0%, #15803d 100%); padding: 30px 24px; text-align: center; color: #ffffff;">
            <h1 style="margin: 0; font-size: 26px; font-weight: 700;">Hair<span style="color: #d9a441;">Bloom</span></h1>
            <p style="margin: 8px 0 0; color: #d1fae5; font-size: 14px;">New Contact Us Form Submission</p>
        </div>
        <div style="padding: 30px 24px;">
            <h2 style="margin-top: 0; color: #111827; font-size: 18px; border-bottom: 2px solid #f3f4f6; padding-bottom: 10px;">Contact Details</h2>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 24px;">
                <tr>
                    <td style="padding: 10px 0; color: #6b7280; font-weight: 600; font-size: 13px; text-transform: uppercase; width: 110px; border-bottom: 1px solid #f3f4f6;">Name:</td>
                    <td style="padding: 10px 0; color: #111827; font-size: 15px; font-weight: 600; border-bottom: 1px solid #f3f4f6;">{escape(name)}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; color: #6b7280; font-weight: 600; font-size: 13px; text-transform: uppercase; border-bottom: 1px solid #f3f4f6;">Email:</td>
                    <td style="padding: 10px 0; font-size: 15px; border-bottom: 1px solid #f3f4f6;"><a href="mailto:{escape(email)}" style="color: #15803d; text-decoration: none; font-weight: 600;">{escape(email)}</a></td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; color: #6b7280; font-weight: 600; font-size: 13px; text-transform: uppercase; border-bottom: 1px solid #f3f4f6;">Phone:</td>
                    <td style="padding: 10px 0; color: #111827; font-size: 15px; border-bottom: 1px solid #f3f4f6;">{escape(phone) if phone else '<span style="color:#9ca3af;">Not provided</span>'}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; color: #6b7280; font-weight: 600; font-size: 13px; text-transform: uppercase; border-bottom: 1px solid #f3f4f6;">Subject:</td>
                    <td style="padding: 10px 0; color: #111827; font-size: 15px; border-bottom: 1px solid #f3f4f6;">{escape(subject) if subject else '<span style="color:#9ca3af;">General Inquiry</span>'}</td>
                </tr>
            </table>
            
            <div style="font-size: 13px; font-weight: 700; color: #6b7280; margin-bottom: 8px; text-transform: uppercase;">Message Content:</div>
            <div style="background: #f9fafb; border-left: 4px solid #15803d; border-radius: 8px; padding: 16px 20px; font-size: 15px; line-height: 1.6; color: #1f2937; white-space: pre-wrap;">{escape(message)}</div>
            
            <div style="margin-top: 25px; text-align: center;">
                <a href="mailto:{escape(email)}?subject=Re: {escape(subject or 'Your Inquiry')}" style="display: inline-block; background-color: #15803d; color: #ffffff !important; padding: 12px 28px; border-radius: 9999px; text-decoration: none; font-weight: 600; font-size: 14px;">Reply to {escape(name)}</a>
            </div>
        </div>
        <div style="background: #f9fafb; padding: 16px 24px; text-align: center; font-size: 12px; color: #9ca3af; border-top: 1px solid #f3f4f6;">
            Sent automatically to {escape(admin_email)} from your HairBloom website.
        </div>
    </div>
</body>
</html>"""

    def _send():
        try:
            send_mail(
                subject=mail_subject,
                message=plain_text,
                from_email=from_email,
                recipient_list=[admin_email],
                html_message=html_content,
                fail_silently=False,
            )
            logger.info("Contact notification email sent successfully to %s", admin_email)
        except Exception as e:
            logger.error("Failed to send contact notification email: %s", e, exc_info=True)

    threading.Thread(target=_send, daemon=True).start()


def contact(request):
    if request.method == "POST" and request.POST.get("form_type") == "contact":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        if name and email and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            # Send notification email to admin
            send_contact_notification(name, email, phone, subject, message)
            
            messages.success(request, "Thank you! Your message has been sent successfully. We will contact you soon.")

        return redirect('contact')

    return render(request, "contact.html")


def formula_page(request):
    products = Product.objects.filter(is_available=True).order_by('price')
    product = products.first()
    formula = FormulaSection.objects.first()
    benefits = Benefit.objects.all()
    return render(request, "formula.html", {
        "products": products,
        "product": product,
        "formula": formula,
        "benefits": benefits,
    })


def about(request):
    product = Product.objects.filter(is_available=True).first()
    return render(request, "about.html", {
        "product": product
    })


def shop(request):
    products = Product.objects.filter(is_available=True).order_by('price')
    product = products.first()
    return render(request, "shop.html", {
        "products": products,
        "product": product,
    })


from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse

@login_required(login_url='home')
def dashboard(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')

    user_email = request.user.email
    orders = Order.objects.filter(email__iexact=user_email).order_by('-created_at') if user_email else Order.objects.none()
    if not orders.exists():
        orders = Order.objects.filter(full_name__icontains=request.user.username).order_by('-created_at')
    
    total_orders = orders.count()
    total_spent = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    active_orders = orders.filter(status__in=['pending', 'confirmed', 'shipped']).count()
    latest_order = orders.first()
    products = Product.objects.filter(is_available=True)[:4]

    return render(request, "dashboard.html", {
        "orders": orders,
        "total_orders": total_orders,
        "total_spent": total_spent,
        "active_orders": active_orders,
        "latest_order": latest_order,
        "products": products,
    })


def login_view(request):
    if request.method == "POST":
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            username_or_email = data.get("username", "").strip()
            password = data.get("password", "")
        else:
            username_or_email = request.POST.get("username", "").strip()
            password = request.POST.get("password", "")

        if not username_or_email or not password:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({"success": False, "message": "Please enter both email/username and password."}, status=400)
            messages.error(request, "Please enter both email/username and password.")
            return redirect('home')

        # Check if login identifier is email
        user_obj = None
        if '@' in username_or_email:
            user_obj = User.objects.filter(email__iexact=username_or_email).first()
            if user_obj:
                username_or_email = user_obj.username

        user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            auth_login(request, user)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({"success": True, "message": "Logged in successfully!", "redirect_url": "/dashboard/"})
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({"success": False, "message": "Invalid email/username or password."}, status=400)
            messages.error(request, "Invalid email/username or password.")
            return redirect('home')

    return redirect('home')


def register_view(request):
    if request.method == "POST":
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            full_name = data.get("full_name", "").strip()
            email = data.get("email", "").strip()
            password = data.get("password", "")
        else:
            full_name = request.POST.get("full_name", "").strip()
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password", "")

        if not email or not password:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({"success": False, "message": "Email and password are required."}, status=400)
            messages.error(request, "Email and password are required.")
            return redirect('home')

        username = email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        if User.objects.filter(email__iexact=email).exists():
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({"success": False, "message": "An account with this email already exists. Please login."}, status=400)
            messages.error(request, "An account with this email already exists.")
            return redirect('home')

        first_name = full_name.split()[0] if full_name else ""
        last_name = " ".join(full_name.split()[1:]) if full_name and len(full_name.split()) > 1 else ""

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        auth_login(request, user)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({"success": True, "message": "Account created successfully!", "redirect_url": "/dashboard/"})

        messages.success(request, f"Welcome {user.username}! Your account has been created.")
        return redirect('dashboard')

    return redirect('home')


def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


def privacy_policy(request):
    return render(request, "privacy_policy.html")


def terms_conditions(request):
    return render(request, "terms_conditions.html")


def refund_policy(request):
    return render(request, "refund_policy.html")


def orders_list(request):
    """
    Admin-style orders management page.
    Shows all orders from PostgreSQL with search & status filter.
    Only accessible to staff/superusers.
    """
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        from django.contrib.auth.decorators import login_required
        messages.error(request, "Access denied. Admin only area.")
        return redirect('home')

    # ---- Filters ----
    status_filter = request.GET.get('status', '').strip()
    search_query  = request.GET.get('q', '').strip()

    orders = Order.objects.prefetch_related('items').order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter)

    if search_query:
        orders = orders.filter(
            models.Q(full_name__icontains=search_query) |
            models.Q(phone__icontains=search_query)     |
            models.Q(email__icontains=search_query)     |
            models.Q(city__icontains=search_query)
        )

    # ---- Summary stats ----
    from django.db.models import Sum, Count
    total_orders    = orders.count()
    total_revenue   = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    pending_count   = orders.filter(status='pending').count()
    delivered_count = orders.filter(status='delivered').count()

    return render(request, "orders.html", {
        "orders":         orders,
        "status_filter":  status_filter,
        "search_query":   search_query,
        "total_orders":   total_orders,
        "total_revenue":  total_revenue,
        "pending_count":  pending_count,
        "delivered_count": delivered_count,
        "status_choices": Order.STATUS_CHOICES,
    })


# ═══════════════════════════════════════════════════════════════════
#  CUSTOM ADMIN DASHBOARD  –  Only staff / superusers
# ═══════════════════════════════════════════════════════════════════

def _admin_required(request):
    """Return True if user is allowed, False otherwise."""
    return request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)


def admin_login(request):
    """Custom admin login page."""
    if _admin_required(request):
        return redirect('admin_dashboard')

    error = None
    if request.method == "POST":
        from django.contrib.auth import authenticate, login as auth_login
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None and (user.is_staff or user.is_superuser):
            auth_login(request, user)
            return redirect('admin_dashboard')
        else:
            error = "Invalid credentials or you don't have admin access."

    return render(request, "admin_login.html", {"error": error})


def admin_logout(request):
    """Logout from custom admin."""
    auth_logout(request)
    messages.info(request, "You have been logged out of the Admin Dashboard.")
    return redirect('admin_login')


def admin_dashboard(request):
    """Main custom admin panel overview."""
    if not _admin_required(request):
        return redirect('admin_login')

    from django.db.models import Sum, Count
    from django.utils import timezone
    import datetime

    today = timezone.now().date()
    week_ago = today - datetime.timedelta(days=7)

    total_orders    = Order.objects.count()
    total_revenue   = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    pending_orders  = Order.objects.filter(status='pending').count()
    total_products  = Product.objects.count()
    total_reviews   = Review.objects.filter(is_approved=True).count()
    total_messages  = ContactMessage.objects.count()
    recent_orders   = Order.objects.prefetch_related('items').order_by('-created_at')[:8]
    recent_messages = ContactMessage.objects.order_by('-created_at')[:5]
    week_orders     = Order.objects.filter(created_at__date__gte=week_ago).count()
    week_revenue    = Order.objects.filter(created_at__date__gte=week_ago).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    return render(request, "admin_dashboard.html", {
        "section": "overview",
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "pending_orders": pending_orders,
        "total_products": total_products,
        "total_reviews": total_reviews,
        "total_messages": total_messages,
        "recent_orders": recent_orders,
        "recent_messages": recent_messages,
        "week_orders": week_orders,
        "week_revenue": week_revenue,
    })


# ─── ORDERS ───────────────────────────────────────────────────────

def admin_orders(request):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')

    from django.db.models import Sum
    status_filter = request.GET.get('status', '').strip()
    search_query  = request.GET.get('q', '').strip()

    orders = Order.objects.prefetch_related('items').order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter)
    if search_query:
        orders = orders.filter(
            models.Q(full_name__icontains=search_query) |
            models.Q(phone__icontains=search_query)     |
            models.Q(email__icontains=search_query)     |
            models.Q(city__icontains=search_query)      |
            models.Q(id__icontains=search_query)
        )

    total_revenue = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    return render(request, "admin_dashboard.html", {
        "section": "orders",
        "orders": orders,
        "status_filter": status_filter,
        "search_query": search_query,
        "total_revenue": total_revenue,
        "status_choices": Order.STATUS_CHOICES,
    })


def admin_order_update_status(request, order_id):
    if not _admin_required(request):
        return JsonResponse({"success": False, "message": "Access denied."}, status=403)
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get("status", "").strip()
        valid = [c[0] for c in Order.STATUS_CHOICES]
        if new_status in valid:
            order.status = new_status
            order.save()
            return JsonResponse({"success": True, "new_status": order.get_status_display()})
    return JsonResponse({"success": False}, status=400)


def admin_order_delete(request, order_id):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        order.delete()
        messages.success(request, f"Order #{order_id} deleted successfully.")
    return redirect('admin_orders')


# ─── PRODUCTS ─────────────────────────────────────────────────────

def admin_products(request):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')

    search_query = request.GET.get('q', '').strip()
    products = Product.objects.all().order_by('id')
    if search_query:
        products = products.filter(
            models.Q(name__icontains=search_query) |
            models.Q(size__icontains=search_query)
        )

    return render(request, "admin_dashboard.html", {
        "section": "products",
        "products": products,
        "search_query": search_query,
    })


def admin_product_add(request):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')

    if request.method == "POST":
        try:
            p = Product(
                name=request.POST.get("name", "").strip(),
                size=request.POST.get("size", "50ml").strip(),
                subtitle=request.POST.get("subtitle", "").strip() or None,
                badge=request.POST.get("badge", "").strip() or None,
                price=request.POST.get("price", 0),
                old_price=request.POST.get("old_price", "") or None,
                discount=request.POST.get("discount", 0),
                description=request.POST.get("description", "").strip(),
                delivery_text=request.POST.get("delivery_text", "Free delivery on orders above Rs. 2,500").strip(),
                is_featured="is_featured" in request.POST,
                is_available="is_available" in request.POST,
            )
            if request.FILES.get("image"):
                p.image = request.FILES["image"]
            p.save()
            messages.success(request, f"Product '{p.name}' added successfully!")
        except Exception as e:
            messages.error(request, f"Error adding product: {e}")
        return redirect('admin_products')

    return render(request, "admin_dashboard.html", {
        "section": "product_form",
        "form_title": "Add New Product",
        "form_action": "add",
    })


def admin_product_edit(request, pk):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')

    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        try:
            product.name = request.POST.get("name", product.name).strip()
            product.size = request.POST.get("size", product.size).strip()
            product.subtitle = request.POST.get("subtitle", "").strip() or None
            product.badge = request.POST.get("badge", "").strip() or None
            product.price = request.POST.get("price", product.price)
            old_p = request.POST.get("old_price", "")
            product.old_price = old_p if old_p else None
            product.discount = request.POST.get("discount", product.discount)
            product.description = request.POST.get("description", product.description).strip()
            product.delivery_text = request.POST.get("delivery_text", product.delivery_text).strip()
            product.is_featured = "is_featured" in request.POST
            product.is_available = "is_available" in request.POST
            if request.FILES.get("image"):
                product.image = request.FILES["image"]
            product.save()
            messages.success(request, f"Product '{product.name}' updated!")
        except Exception as e:
            messages.error(request, f"Error updating product: {e}")
        return redirect('admin_products')

    return render(request, "admin_dashboard.html", {
        "section": "product_form",
        "form_title": f"Edit Product: {product.name}",
        "form_action": "edit",
        "product": product,
    })


def admin_product_delete(request, pk):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')
    if request.method == "POST":
        product = get_object_or_404(Product, pk=pk)
        name = product.name
        product.delete()
        messages.success(request, f"Product '{name}' deleted.")
    return redirect('admin_products')


# ─── REVIEWS ──────────────────────────────────────────────────────

def admin_reviews(request):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')

    search_query = request.GET.get('q', '').strip()
    reviews = Review.objects.all().order_by('-created_at')
    if search_query:
        reviews = reviews.filter(
            models.Q(name__icontains=search_query) |
            models.Q(comment__icontains=search_query) |
            models.Q(city__icontains=search_query)
        )

    return render(request, "admin_dashboard.html", {
        "section": "reviews",
        "reviews": reviews,
        "search_query": search_query,
    })


def admin_review_toggle(request, pk):
    if not _admin_required(request):
        return JsonResponse({"success": False}, status=403)
    if request.method == "POST":
        review = get_object_or_404(Review, pk=pk)
        review.is_approved = not review.is_approved
        review.save()
        return JsonResponse({"success": True, "is_approved": review.is_approved})
    return JsonResponse({"success": False}, status=400)


def admin_review_delete(request, pk):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')
    if request.method == "POST":
        review = get_object_or_404(Review, pk=pk)
        review.delete()
        messages.success(request, "Review deleted.")
    return redirect('admin_reviews')


# ─── CONTACT MESSAGES ─────────────────────────────────────────────

def admin_messages(request):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')

    search_query = request.GET.get('q', '').strip()
    contact_msgs = ContactMessage.objects.order_by('-created_at')
    if search_query:
        contact_msgs = contact_msgs.filter(
            models.Q(name__icontains=search_query) |
            models.Q(email__icontains=search_query) |
            models.Q(subject__icontains=search_query)
        )

    return render(request, "admin_dashboard.html", {
        "section": "messages",
        "contact_msgs": contact_msgs,
        "search_query": search_query,
    })


def admin_message_delete(request, pk):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')
    if request.method == "POST":
        msg = get_object_or_404(ContactMessage, pk=pk)
        msg.delete()
        messages.success(request, "Message deleted.")
    return redirect('admin_messages')


# ─── BENEFITS ─────────────────────────────────────────────────────

def admin_benefits(request):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')

    benefits = Benefit.objects.all().order_by('id')
    return render(request, "admin_dashboard.html", {
        "section": "benefits",
        "benefits": benefits,
    })


def admin_benefit_add(request):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')

    if request.method == "POST":
        try:
            Benefit.objects.create(
                title=request.POST.get("title", "").strip(),
                description=request.POST.get("description", "").strip(),
                icon=request.POST.get("icon", "droplet").strip(),
            )
            messages.success(request, "Benefit added!")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect('admin_benefits')

    return render(request, "admin_dashboard.html", {
        "section": "benefit_form",
        "form_title": "Add Benefit",
        "form_action": "add",
    })


def admin_benefit_edit(request, pk):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')

    benefit = get_object_or_404(Benefit, pk=pk)

    if request.method == "POST":
        benefit.title = request.POST.get("title", benefit.title).strip()
        benefit.description = request.POST.get("description", benefit.description).strip()
        benefit.icon = request.POST.get("icon", benefit.icon).strip()
        benefit.save()
        messages.success(request, "Benefit updated!")
        return redirect('admin_benefits')

    return render(request, "admin_dashboard.html", {
        "section": "benefit_form",
        "form_title": f"Edit Benefit: {benefit.title}",
        "form_action": "edit",
        "benefit": benefit,
    })


def admin_benefit_delete(request, pk):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')
    if request.method == "POST":
        benefit = get_object_or_404(Benefit, pk=pk)
        benefit.delete()
        messages.success(request, "Benefit deleted.")
    return redirect('admin_benefits')


# ════════════════════════════════════════════════════════════════
# HERO SECTION MANAGEMENT
# ════════════════════════════════════════════════════════════════

def admin_hero(request):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')

    hero = Hero.objects.first()
    return render(request, "admin_dashboard.html", {
        "section": "hero",
        "hero": hero,
    })


def admin_hero_edit(request):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')

    hero = Hero.objects.first()

    if request.method == "POST":
        if not hero:
            hero = Hero()

        # Main Content
        hero.heading = request.POST.get("heading", "").strip()
        hero.heading_green = request.POST.get("heading_green", "").strip()
        hero.sub_heading = request.POST.get("sub_heading", "").strip()
        hero.button_text = request.POST.get("button_text", "Shop Now").strip()
        hero.button_link = request.POST.get("button_link", "#shop").strip()

        # Badge
        hero.badge_text = request.POST.get("badge_text", "100% Natural Hair Care").strip()

        # Trust Points
        hero.trust_point_1 = request.POST.get("trust_point_1", "Natural").strip()
        hero.trust_point_2 = request.POST.get("trust_point_2", "Chemical Free").strip()
        hero.trust_point_3 = request.POST.get("trust_point_3", "Cruelty Free").strip()

        # Floating Card
        hero.floating_card_label = request.POST.get("floating_card_label", "Natural Care").strip()
        hero.floating_card_value = request.POST.get("floating_card_value", "For Healthy Hair").strip()

        # Rating Card
        hero.rating_card_text = request.POST.get("rating_card_text", "Loved by customers").strip()

        # Image (only update if new file uploaded)
        if request.FILES.get("image"):
            hero.image = request.FILES["image"]

        hero.save()
        messages.success(request, "Hero Section updated successfully!")
        return redirect('admin_hero')

    return render(request, "admin_dashboard.html", {
        "section": "hero_form",
        "form_title": "Edit Hero Section",
        "hero": hero,
    })


# ════════════════════════════════════════════════════════════════
# BLOG / JOURNAL
# ════════════════════════════════════════════════════════════════

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    related_posts = BlogPost.objects.filter(
        is_published=True
    ).exclude(id=post.id)[:3]

    return render(request, "blog_detail.html", {
        "post": post,
        "related_posts": related_posts,
    })


# ════════════════════════════════════════════════════════════════
# ADMIN - BLOG MANAGEMENT
# ════════════════════════════════════════════════════════════════

def admin_blogs(request):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')

    posts = BlogPost.objects.all().order_by('-created_at')
    return render(request, "admin_dashboard.html", {
        "section": "blogs",
        "blog_posts_list": posts,
    })


def admin_blog_add(request):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')

    if request.method == "POST":
        from django.utils.text import slugify
        title = request.POST.get("title", "").strip()
        slug = slugify(title)

        # Ensure unique slug
        base_slug = slug
        counter = 1
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        try:
            BlogPost.objects.create(
                title=title,
                slug=slug,
                excerpt=request.POST.get("excerpt", "").strip(),
                content=request.POST.get("content", "").strip(),
                category=request.POST.get("category", "hair_care"),
                author=request.POST.get("author", "HairGlow Team").strip(),
                read_time=int(request.POST.get("read_time", 5)),
                is_published=request.POST.get("is_published") == "on",
                is_featured=request.POST.get("is_featured") == "on",
                image=request.FILES.get("image"),
            )
            messages.success(request, "Blog post added!")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect('admin_blogs')

    return render(request, "admin_dashboard.html", {
        "section": "blog_form",
        "form_title": "Add Blog Post",
        "form_action": "add",
    })


def admin_blog_edit(request, pk):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')

    post = get_object_or_404(BlogPost, pk=pk)

    if request.method == "POST":
        post.title = request.POST.get("title", post.title).strip()
        post.excerpt = request.POST.get("excerpt", post.excerpt).strip()
        post.content = request.POST.get("content", post.content).strip()
        post.category = request.POST.get("category", post.category)
        post.author = request.POST.get("author", post.author).strip()
        post.read_time = int(request.POST.get("read_time", post.read_time))
        post.is_published = request.POST.get("is_published") == "on"
        post.is_featured = request.POST.get("is_featured") == "on"

        if request.FILES.get("image"):
            post.image = request.FILES["image"]

        post.save()
        messages.success(request, "Blog post updated!")
        return redirect('admin_blogs')

    return render(request, "admin_dashboard.html", {
        "section": "blog_form",
        "form_title": f"Edit: {post.title}",
        "form_action": "edit",
        "blog_post": post,
    })


def admin_blog_delete(request, pk):
    if not _admin_required(request):
        messages.error(request, "Access denied.")
        return redirect('admin_login')
    if request.method == "POST":
        post = get_object_or_404(BlogPost, pk=pk)
        post.delete()
        messages.success(request, "Blog post deleted.")
    return redirect('admin_blogs')
