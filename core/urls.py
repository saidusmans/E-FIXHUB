from django.urls import path
from . import views

urlpatterns = [

    # ── Public Pages ──────────────────────────────────────────────
    path('',          views.home,           name='home'),
    path('about/',    views.about,          name='about'),
    path('contact/',  views.contact,        name='contact'),
    path('start/',           views.role_selection,  name='role_selection'),
    path('role-selection/',   views.role_selection),    # alias

    # ── Authentication ────────────────────────────────────────────
    # Login
    path('login/customer/',   views.customer_login,    name='customer_login'),
    path('login/agent/',      views.agent_login,       name='agent_login'),
    path('login/mechanic/',   views.mechanic_login,    name='mechanic_login'),
    path('login/admin/',      views.admin_login,       name='admin_login'),
    path('login/',            views.customer_login,    name='login'),
    path('logout/',           views.logout_view,       name='logout'),

    # Registration
    path('register/customer/',  views.customer_register,   name='customer_register'),
    path('register/agent/',     views.agent_register,      name='agent_register'),
    path('register/mechanic/',  views.mechanic_register,   name='mechanic_register'),

    # ── Dashboard Router ──────────────────────────────────────────
    path('dashboard/', views.dashboard, name='dashboard'),

    # ── Customer ──────────────────────────────────────────────────
    path('customer/dashboard/',      views.customer_dashboard,    name='customer_dashboard'),
    path('customer/upload/',         views.customer_upload,       name='customer_upload'),
    path('customer/my-products/',    views.customer_my_products,  name='my_products'),
    path('customer/my-orders/',      views.customer_my_orders,    name='my_orders'),
    path('upload/',                  views.customer_upload,       name='item_upload'),

    # ── Store ─────────────────────────────────────────────────────
    path('store/',                     views.browse_store,         name='browse_store'),
    path('store/<int:pk>/',            views.product_detail_view,  name='product_detail_view'),
    path('purchase/<int:pk>/',         views.customer_buy,         name='purchase_product'),
    path('buy/<int:pk>/',              views.customer_buy,         name='buy_product'),

    # ── Agent ─────────────────────────────────────────────────────
    path('agent/dashboard/',             views.agent_dashboard,              name='agent_dashboard'),
    path('agent/collect/<int:pk>/',      views.agent_mark_collected,         name='mark_collected'),
    path('agent/dispatch-order/<int:pk>/', views.agent_dispatch_order,      name='agent_dispatch_order'),
    path('agent/deliver/<int:pk>/',      views.agent_mark_delivered,         name='mark_delivered'),
    path('agent/item/<int:pk>/',          views.agent_item_detail,             name='agent_item_detail'),
    path('agent/collections/',           views.agent_assigned_collections,   name='assigned_collections'),
    path('agent/deliveries/',            views.agent_delivery_management,    name='delivery_management'),

    # ── Mechanic ──────────────────────────────────────────────────
    path('mechanic/dashboard/',          views.mechanic_dashboard,        name='mechanic_dashboard'),
    path('mechanic/repair/<int:pk>/',    views.mechanic_repair,           name='repair_item'),
    path('mechanic/repairs/',            views.mechanic_assigned_repairs,  name='assigned_repairs'),

    # ── Admin Panel ───────────────────────────────────────────────
    path('admin-panel/',                             views.admin_dashboard,          name='admin_dashboard'),
    path('admin-panel/approve-item/<int:pk>/',       views.admin_approve_item,       name='approve_item'),
    path('admin-panel/reject-item/<int:pk>/',        views.admin_reject_item,        name='reject_item'),
    path('admin-panel/assign-agent/<int:pk>/',       views.admin_assign_agent,       name='assign_agent'),
    path('admin-panel/assign-mechanic/<int:pk>/',    views.admin_assign_mechanic,    name='assign_mechanic'),
    path('admin-panel/assign-retrieval/<int:pk>/',   views.admin_assign_retrieval_agent, name='assign_retrieval_agent'),
    path('admin-panel/request-rework/<int:pk>/',     views.admin_request_rework,     name='request_rework'),
    path('admin-panel/publish-product/<int:pk>/',    views.admin_publish_product,    name='publish_product'),
    path('admin-panel/assign-delivery/<int:pk>/',    views.admin_assign_delivery_agent, name='assign_delivery'),

    # User management
    path('admin-panel/users/',                                   views.admin_manage_users,     name='manage_users'),
    path('admin-panel/users/<int:pk>/',                          views.admin_user_detail,      name='user_detail'),
    path('admin-panel/users/delete/<int:pk>/',                   views.admin_delete_user,      name='delete_user'),
    path('admin-panel/users/approve/<int:pk>/<str:role>/',       views.admin_approve_profile,  name='approve_profile'),
    path('admin-panel/users/toggle-status/<int:pk>/',            views.admin_toggle_user_status, name='toggle_user_status'),
    path('admin-panel/users/revoke-credentials/<int:pk>/',       views.admin_revoke_credentials, name='revoke_credentials'),

    # Products
    path('admin-panel/products/',     views.admin_manage_products,    name='manage_products'),
    path('admin-panel/published/',    views.admin_published_products, name='published_products'),
    path('admin-panel/items/<int:pk>/', views.admin_item_detail,    name='admin_item_detail'),

    # Orders
    path('admin-panel/orders/',       views.admin_orders,        name='orders'),

    # Activity
    path('admin-panel/logs/',         views.admin_activity_logs, name='activity_logs'),
    path('admin-panel/analytics/',    views.admin_analytics,     name='admin_analytics'),
    path('admin-panel/export/',       views.export_inventory_csv, name='export_inventory_csv'),

    # Financial Settlements
    path('admin-panel/payments/',          views.admin_mechanic_payments, name='admin_mechanic_payments'),
    path('admin-panel/pay/<int:pk>/',      views.admin_pay_mechanic,      name='admin_pay_mechanic'),
]
