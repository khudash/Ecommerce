from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('contact/', views.contact, name='contact'),
    path('formula/', views.formula_page, name='formula'),
    path('about/', views.about, name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-and-conditions/', views.terms_conditions, name='terms_conditions'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('orders/', views.orders_list, name='orders_list'),
    path('submit-review/', views.submit_review, name='submit_review'),

    # ─── Custom Admin Dashboard ─────────────────────────────────────
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/login/', views.admin_login, name='admin_login'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),

    # Orders CRUD
    path('admin-panel/orders/', views.admin_orders, name='admin_orders'),
    path('admin-panel/orders/<int:order_id>/update-status/', views.admin_order_update_status, name='admin_order_update_status'),
    path('admin-panel/orders/<int:order_id>/delete/', views.admin_order_delete, name='admin_order_delete'),

    # Products CRUD
    path('admin-panel/products/', views.admin_products, name='admin_products'),
    path('admin-panel/products/add/', views.admin_product_add, name='admin_product_add'),
    path('admin-panel/products/<int:pk>/edit/', views.admin_product_edit, name='admin_product_edit'),
    path('admin-panel/products/<int:pk>/delete/', views.admin_product_delete, name='admin_product_delete'),

    # Reviews CRUD
    path('admin-panel/reviews/', views.admin_reviews, name='admin_reviews'),
    path('admin-panel/reviews/<int:pk>/toggle/', views.admin_review_toggle, name='admin_review_toggle'),
    path('admin-panel/reviews/<int:pk>/delete/', views.admin_review_delete, name='admin_review_delete'),

    # Contact Messages
    path('admin-panel/messages/', views.admin_messages, name='admin_messages'),
    path('admin-panel/messages/<int:pk>/delete/', views.admin_message_delete, name='admin_message_delete'),

    # Benefits CRUD
    path('admin-panel/benefits/', views.admin_benefits, name='admin_benefits'),
    path('admin-panel/benefits/add/', views.admin_benefit_add, name='admin_benefit_add'),
    path('admin-panel/benefits/<int:pk>/edit/', views.admin_benefit_edit, name='admin_benefit_edit'),
    path('admin-panel/benefits/<int:pk>/delete/', views.admin_benefit_delete, name='admin_benefit_delete'),

    # Hero Section
    path('admin-panel/hero/', views.admin_hero, name='admin_hero'),
    path('admin-panel/hero/edit/', views.admin_hero_edit, name='admin_hero_edit'),

    # Blog / Journal
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),

    # Admin Blog CRUD
    path('admin-panel/blogs/', views.admin_blogs, name='admin_blogs'),
    path('admin-panel/blogs/add/', views.admin_blog_add, name='admin_blog_add'),
    path('admin-panel/blogs/<int:pk>/edit/', views.admin_blog_edit, name='admin_blog_edit'),
    path('admin-panel/blogs/<int:pk>/delete/', views.admin_blog_delete, name='admin_blog_delete'),
]
