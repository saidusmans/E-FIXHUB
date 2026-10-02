"""
E-Fix Hub — Views (Complete Workflow Engine)
=============================================
Role Routing:   Admin → admin_dashboard   |  Customer → customer_dashboard
                Agent → agent_dashboard   |  Mechanic → mechanic_dashboard

Chain of Custody:
  Customer uploads → Admin approves → Admin assigns Agent → Agent collects
  → Admin assigns Mechanic → Mechanic repairs (auto-creates Product)
  → Admin publishes → Customer buys → Agent delivers → Done
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Q
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator

from .models import (
    CustomUser, EWasteItem, RepairLog, Product, Order,
    Notification, ActivityLog, CustomerProfile, AgentProfile,
    MechanicProfile, Gallery
)
from .forms import (
    CustomerRegistrationForm, AgentRegistrationForm, MechanicRegistrationForm,
    EWasteUploadForm, RepairLogForm
)


# ═══════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def log(user, action, category='general'):
    """Improved audit logging with categories."""
    full_action = f"[{category.upper()}] {action}"
    ActivityLog.objects.create(user=user, action=full_action)
    print(f"Audit Log: {user.username} - {full_action}")

def notify(user, message):
    Notification.objects.create(user=user, message=message)

def notify_admins(message):
    admins = CustomUser.objects.filter(Q(role='ADMIN') | Q(is_superuser=True))
    for admin in admins:
        Notification.objects.create(user=admin, message=message)

def is_admin(user):    return user.is_authenticated and (user.role == 'ADMIN' or user.is_superuser)
def is_customer(user): return user.is_authenticated and user.role == 'CUSTOMER'
def is_agent(user):    return user.is_authenticated and user.role == 'AGENT'
def is_mechanic(user): return user.is_authenticated and user.role == 'MECHANIC'

def role_redirect(request):
    """Redirect to the correct dashboard based on role."""
    role = request.user.role
    if role == 'ADMIN' or request.user.is_superuser:
        return redirect('admin_dashboard')
    elif role == 'AGENT':
        return redirect('agent_dashboard')
    elif role == 'MECHANIC':
        return redirect('mechanic_dashboard')
    else:
        return redirect('customer_dashboard')


# ═══════════════════════════════════════════════════════════════════
# PUBLIC / AUTH VIEWS
# ═══════════════════════════════════════════════════════════════════

def home(request):
    featured = Product.objects.filter(is_published=True, is_sold=False)[:4]
    gallery  = Gallery.objects.all()[:6]
    return render(request, 'core/home/index.html', {
        'featured_products': featured,
        'gallery_items': gallery,
    })

def about(request):
    return render(request, 'core/home/about.html')

def contact(request):
    return render(request, 'core/home/contact.html')

def role_selection(request):
    if request.user.is_authenticated:
        return role_redirect(request)
    return render(request, 'core/auth/role_selection.html')


# ─── LOGIN ────────────────────────────────────────────────────────

def _login_view(request, role, template):
    if request.user.is_authenticated:
        return role_redirect(request)
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            if user.role != role and not (role == 'ADMIN' and user.is_superuser):
                messages.error(request, f"This login is only for {role}s. Please use the correct portal.")
                return render(request, template, {'role': role})
            auth_login(request, user)
            log(user, f"{role} logged in")
            return role_redirect(request)
        messages.error(request, "Invalid username or password.")
    return render(request, template, {'role': role})

def customer_login(request):
    return _login_view(request, 'CUSTOMER', 'core/auth/customer_login.html')

def agent_login(request):
    return _login_view(request, 'AGENT', 'core/auth/agent_login.html')

def mechanic_login(request):
    return _login_view(request, 'MECHANIC', 'core/auth/mechanic_login.html')

def admin_login(request):
    if request.user.is_authenticated:
        return role_redirect(request)
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user and (user.role == 'ADMIN' or user.is_superuser):
            auth_login(request, user)
            log(user, "Admin logged in")
            return redirect('admin_dashboard')
        messages.error(request, "Invalid admin credentials.")
    return render(request, 'core/auth/admin_login.html')

def logout_view(request):
    if request.user.is_authenticated:
        log(request.user, f"{request.user.role} logged out")
    auth_logout(request)
    return redirect('home')


# ─── REGISTRATION ─────────────────────────────────────────────────

def customer_register(request):
    if request.user.is_authenticated:
        return role_redirect(request)
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            log(user, "Customer registered")
            notify_admins(f"New Signal: @{user.username} (CUSTOMER) registered from {user.district}, {user.state}")
            messages.success(request, "Account created! Please log in.")
            return redirect('customer_login')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'core/auth/customer_register.html', {'form': form})

def agent_register(request):
    if request.user.is_authenticated:
        return role_redirect(request)
    if request.method == 'POST':
        form = AgentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            log(user, "Agent registered — pending verification")
            notify_admins(f"High Alert: New Agent @{user.username} applied from {user.district}, {user.state}. Review credentials.")
            messages.success(request, "Application submitted! Admin will verify your account.")
            return redirect('agent_login')
    else:
        form = AgentRegistrationForm()
    return render(request, 'core/auth/agent_register.html', {'form': form})

def mechanic_register(request):
    if request.user.is_authenticated:
        return role_redirect(request)
    if request.method == 'POST':
        form = MechanicRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            log(user, "Mechanic registered — pending verification")
            notify_admins(f"High Alert: New Mechanic @{user.username} applied from {user.district}, {user.state}. Review workstation setup.")
            messages.success(request, "Application submitted! Admin will verify your account.")
            return redirect('mechanic_login')
    else:
        form = MechanicRegistrationForm()
    return render(request, 'core/auth/mechanic_register.html', {'form': form})


# ─── UNIFIED DASHBOARD ROUTER ─────────────────────────────────────

@login_required
def dashboard(request):
    return role_redirect(request)


# ═══════════════════════════════════════════════════════════════════
# CUSTOMER VIEWS
# ═══════════════════════════════════════════════════════════════════

@login_required
@user_passes_test(is_customer, login_url='/login/customer/')
def customer_dashboard(request):
    my_items      = EWasteItem.objects.filter(uploaded_by=request.user)
    my_orders     = Order.objects.filter(buyer=request.user).select_related('product__linked_item')
    store_items   = Product.objects.filter(is_published=True, is_sold=False)[:3]
    notifications = request.user.notifications.filter(is_read=False)[:5]
    return render(request, 'core/dashboard/customer/customer_dashboard.html', {
        'my_items':       my_items,
        'my_orders':      my_orders,
        'store_products': store_items,
        'notifications':  notifications,
    })

@login_required
@user_passes_test(is_customer, login_url='/login/customer/')
def customer_upload(request):
    if request.method == 'POST':
        form = EWasteUploadForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.uploaded_by = request.user
            item.status = 'uploaded'
            item.save()
            log(request.user, f"Uploaded e-waste: {item.title}")
            messages.success(request, f"'{item.title}' has been submitted for review.")
            return redirect('customer_dashboard')
    else:
        form = EWasteUploadForm()
    return render(request, 'core/dashboard/customer/customer_upload_product.html', {'form': form})

@login_required
@user_passes_test(is_customer, login_url='/login/customer/')
def customer_my_products(request):
    my_items = EWasteItem.objects.filter(uploaded_by=request.user)
    return render(request, 'core/dashboard/customer/customer_my_products.html', {'my_items': my_items})

@login_required
@user_passes_test(is_customer, login_url='/login/customer/')
def customer_my_orders(request):
    orders = Order.objects.filter(buyer=request.user).select_related('product__linked_item', 'assigned_agent').order_by('-created_at')
    return render(request, 'core/dashboard/customer/customer_my_orders.html', {'orders': orders})

@login_required
@user_passes_test(is_customer, login_url='/login/customer/')
def customer_buy(request, pk):
    product = get_object_or_404(Product, pk=pk, is_published=True, is_sold=False)
    if request.method == 'POST':
        order = Order.objects.create(
            product=product,
            buyer=request.user,
            total_price=product.price,
            shipping_name=request.POST.get('shipping_name'),
            shipping_phone=request.POST.get('shipping_phone'),
            shipping_address=request.POST.get('shipping_address'),
            payment_method=request.POST.get('payment_method', 'COD'),
            status='ordered',
        )
        product.is_sold = True
        product.stock = 0
        product.save()

        # Update lifecycle timestamp
        product.linked_item.status = 'ordered'
        product.linked_item.sold_at = timezone.now()
        product.linked_item.save()

        notify(request.user, f"Acquisition Locked: Order #{order.id} for '{product.linked_item.title}' is being processed for deployment.")
        notify_admins(f"Revenue Signal: New Order #{order.id} placed by @{request.user.username} for ₹{product.price}.")
        log(request.user, f"Purchased product: {product.linked_item.title}")
        messages.success(request, "Purchase successful! Your order is being processed.")
        return redirect('customer_dashboard')
    return render(request, 'core/purchase_confirmation.html', {'product': product})


# ═══════════════════════════════════════════════════════════════════
# AGENT VIEWS
# ═══════════════════════════════════════════════════════════════════

@login_required
@user_passes_test(is_agent, login_url='/login/agent/')
def agent_dashboard(request):
    profile        = getattr(request.user, 'agent_profile', None)
    to_collect     = EWasteItem.objects.filter(assigned_agent=request.user, status__in=['agent_assigned', 'repair_completed']) # Collect from Cust or Retrieve from Mech
    collected      = EWasteItem.objects.filter(assigned_agent=request.user, status='collected')
    assigned_items = EWasteItem.objects.filter(assigned_agent=request.user)
    to_deliver     = Order.objects.filter(assigned_agent=request.user, status__in=['delivery_assigned', 'out_for_delivery'])
    delivered      = Order.objects.filter(assigned_agent=request.user, status='delivered')
    notifications  = request.user.notifications.filter(is_read=False)[:5]
    return render(request, 'core/dashboard/agent/agent_dashboard.html', {
        'profile':        profile,
        'to_collect':     to_collect,
        'collected':      collected,
        'assigned_items': assigned_items,
        'to_deliver':     to_deliver,
        'delivered':      delivered,
        'notifications':  notifications,
    })

@login_required
@user_passes_test(is_agent, login_url='/login/agent/')
def agent_item_detail(request, pk):
    """Logistical intelligence for individual assets."""
    item = get_object_or_404(EWasteItem, pk=pk, assigned_agent=request.user)
    return render(request, 'core/dashboard/agent/agent_item_detail.html', {
        'item': item,
    })

@login_required
@user_passes_test(is_agent, login_url='/login/agent/')
def agent_mark_collected(request, pk):
    item = get_object_or_404(EWasteItem, pk=pk, assigned_agent=request.user)
    if item.status == 'repair_completed': 
        item.status = 'awaiting_admin_approval' # Retrieved from Mechanic, now at Hub
    else:
        item.status = 'collected' # Picked up from customer
        item.collected_at = timezone.now()
    item.save()
    notify(item.uploaded_by, f"Your item '{item.title}' has been collected by Agent {request.user.username}.")
    log(request.user, f"Marked as collected: {item.title}")
    messages.success(request, f"'{item.title}' marked as collected.")
    return redirect('agent_dashboard')

@login_required
@user_passes_test(is_agent, login_url='/login/agent/')
def agent_mark_delivered(request, pk):
    order = get_object_or_404(Order, pk=pk, assigned_agent=request.user)
    order.status = 'delivered'
    order.product.linked_item.status = 'delivered' # Ensure item is also marked delivered
    order.product.linked_item.save()
    order.save()
    notify(order.buyer, f"Your order for '{order.product.linked_item.title}' has been delivered!")
    log(request.user, f"Delivered order #{order.id}")
    messages.success(request, f"Order #{order.id} marked as delivered.")
    return redirect('agent_dashboard')

@login_required
@user_passes_test(is_agent, login_url='/login/agent/')
def agent_assigned_collections(request):
    to_collect = EWasteItem.objects.filter(assigned_agent=request.user, status='agent_assigned')
    collected  = EWasteItem.objects.filter(assigned_agent=request.user, status='collected')
    return render(request, 'core/dashboard/agent/agent_assigned_collections.html', {
        'to_collect': to_collect,
        'collected':  collected,
    })

@login_required
@user_passes_test(is_agent, login_url='/login/agent/')
def agent_delivery_management(request):
    all_deliveries = Order.objects.filter(assigned_agent=request.user, status__in=['ordered', 'delivery_assigned', 'delivered']).order_by('-created_at')
    return render(request, 'core/dashboard/agent/agent_delivery_management.html', {
        'all_deliveries': all_deliveries,
    })


# ═══════════════════════════════════════════════════════════════════
# MECHANIC VIEWS
# ═══════════════════════════════════════════════════════════════════

@login_required
@user_passes_test(is_mechanic, login_url='/login/mechanic/')
def mechanic_dashboard(request):
    profile = getattr(request.user, 'mechanic_profile', None)
    
    # Active nodes
    active_statuses = ['mechanic_assigned', 'repairing', 'repair_completed', 'awaiting_admin_approval']
    pending_repairs = EWasteItem.objects.filter(assigned_mechanic=request.user, status__in=active_statuses)
    
    # Finished nodes
    repaired = EWasteItem.objects.filter(assigned_mechanic=request.user, status__in=['published_in_store', 'ordered', 'delivered'])
    
    notifications = request.user.notifications.filter(is_read=False)[:5]
    
    return render(request, 'core/dashboard/mechanic/mechanic_dashboard.html', {
        'profile': profile,
        'pending_repairs': pending_repairs,
        'repaired': repaired,
        'notifications': notifications,
    })

@login_required
@user_passes_test(is_mechanic, login_url='/login/mechanic/')
def mechanic_repair(request, pk):
    item = get_object_or_404(EWasteItem, pk=pk, assigned_mechanic=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        # Core technical fields
        notes      = request.POST.get('repair_notes')
        parts      = request.POST.get('parts_replaced')
        eta        = request.POST.get('estimated_completion_date')
        progress   = request.POST.get('repair_progress', 0)
        cost       = request.POST.get('cost', 0)

        # Synchronize EWasteItem fields
        item.parts_replaced = parts
        if eta:
            item.estimated_completion_date = eta

        if action == 'update_progress':
            item.repair_progress_percentage = int(progress)
            item.status = 'repairing'
            item.save()
            log(request.user, f"Incremental Update: '{item.title}' at {progress}%")
            
            # Upsert partial RepairLog
            repair, _ = RepairLog.objects.get_or_create(item=item, defaults={'mechanic': request.user, 'cost': 0})
            repair.repair_notes = notes
            if cost: repair.cost = cost
            repair.save()

            messages.success(request, f"Tactical progress synced for '{item.title}'.")
            return redirect('mechanic_dashboard')
            
        elif action == 'complete_restoration':
            # Update EWasteItem to final state
            item.status = 'repair_completed'
            item.repair_progress_percentage = 100
            item.restored_at = timezone.now()
            item.save()

            # Finalize RepairLog
            repair, _ = RepairLog.objects.get_or_create(item=item, defaults={'mechanic': request.user, 'cost': 0})
            repair.repair_notes = notes
            repair.cost = float(cost) if cost else 0
            repair.save()

            log(request.user, f"Final Engineering Audit: {item.title} (Success)")
            notify_admins(f"Audit Result: '{item.title}' by Node @{request.user.username} is mission-ready.")
            messages.success(request, f"Restoration for '{item.title}' finalized and audited. Admin notified.")
            return redirect('mechanic_dashboard')
    
    return render(request, 'core/mechanic_repair_form.html', {'item': item})

@login_required
@user_passes_test(is_mechanic, login_url='/login/mechanic/')
def mechanic_assigned_repairs(request):
    assigned = EWasteItem.objects.filter(assigned_mechanic=request.user, status='mechanic_assigned')
    repaired = EWasteItem.objects.filter(assigned_mechanic=request.user, status='repair_completed')
    return render(request, 'core/dashboard/mechanic/mechanic_assigned_repairs.html', {
        'assigned': assigned,
        'repaired': repaired,
    })


# ═══════════════════════════════════════════════════════════════════
# ADMIN VIEWS
# ═══════════════════════════════════════════════════════════════════

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Refined production-ready administrative command center."""
    from django.db.models import Count, Q # Added imports inside to avoid pollution if not used

    context = {
        # High-Performance Overview metrics
        'total_users':     CustomUser.objects.count(),
        'total_customers': CustomUser.objects.filter(role='CUSTOMER').count(),
        'total_agents':    CustomUser.objects.filter(role='AGENT').count(),
        'total_mechanics': CustomUser.objects.filter(role='MECHANIC').count(),
        'total_items':     EWasteItem.objects.count(),
        'in_store':        Product.objects.filter(is_published=True, is_sold=False).count(),
        'total_orders':    Order.objects.count(),
        'total_revenue':   Order.objects.aggregate(total=Sum('total_price'))['total'] or 0,
        
        # Logistical pipeline monitoring (The 12-Stage Workflow)
        'pending_items':   EWasteItem.objects.filter(status='uploaded').select_related('uploaded_by'),
        'approved_items':  EWasteItem.objects.filter(status='inspection_pending'),
        'collected_items': EWasteItem.objects.filter(status='collected'),
        'active_restorations': EWasteItem.objects.filter(status='repairing').select_related('assigned_mechanic'),
        'restoration_completed': EWasteItem.objects.filter(status='repair_completed'),
        'repaired_items':  EWasteItem.objects.filter(status__in=['awaiting_admin_approval', 'repair_completed']),
        
        # Role verification status
        'pending_agents':    AgentProfile.objects.filter(verification_status='Pending').count(),
        'pending_mechanics': MechanicProfile.objects.filter(verification_status='Pending').count(),
        
        # Operational health metrics
        'under_repair':    EWasteItem.objects.filter(status__in=['mechanic_assigned', 'repairing']).count(),
        
        # Transactional Analysis
        'recent_activities': ActivityLog.objects.all().select_related('user')[:15],
        'top_performing_mechanics': CustomUser.objects.filter(role='MECHANIC').annotate(completed_repairs=Count('repairs_done', filter=Q(repairs_done__item__status='repair_completed'))).order_by('-completed_repairs')[:5],
    }
    return render(request, 'core/dashboard/admin/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_approve_item(request, pk):
    item = get_object_or_404(EWasteItem, pk=pk)
    item.status = 'inspection_pending'
    item.approved_at = timezone.now()
    item.save()
    notify(item.uploaded_by, f"Your item '{item.title}' has been approved.")
    log(request.user, f"Approved item: {item.title}")
    messages.success(request, f"'{item.title}' approved.")
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def admin_reject_item(request, pk):
    item = get_object_or_404(EWasteItem, pk=pk)
    item.status = 'uploaded'
    notify(item.uploaded_by, f"Your item '{item.title}' was reviewed and needs more information.")
    log(request.user, f"Rejected/held item: {item.title}")
    messages.warning(request, f"'{item.title}' sent back for review.")
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def admin_request_rework(request, pk):
    item = get_object_or_404(EWasteItem, pk=pk, status='repair_completed')
    item.status = 'repairing'
    item.repair_progress_percentage = 90 # Revert progress slightly
    item.save()
    
    notify(item.assigned_mechanic, f"Rework Protocol Initiated: Your restoration for '{item.title}' requires additional calibration. Review admin feedback.")
    log(request.user, f"Requested rework for asset: {item.title}")
    messages.warning(request, f"Rework signal sent to Engineer @{item.assigned_mechanic.username}.")
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def admin_assign_agent(request, pk):
    item = get_object_or_404(EWasteItem, pk=pk, status='inspection_pending')
    agents = CustomUser.objects.filter(role='AGENT', agent_profile__verification_status='Approved')
    mechanics = CustomUser.objects.filter(role='MECHANIC', mechanic_profile__verification_status='Approved')
    
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id')
        mechanic_id = request.POST.get('mechanic_id')
        
        agent = get_object_or_404(CustomUser, pk=agent_id, role='AGENT')
        item.assigned_agent = agent
        
        if mechanic_id:
            mechanic = get_object_or_404(CustomUser, pk=mechanic_id, role='MECHANIC')
            item.assigned_mechanic = mechanic
            notify(mechanic, f"Pre-assigned for restoration: '{item.title}' will be delivered by Agent {agent.username} soon.")
            
        item.status = 'agent_assigned'
        item.save()
        
        notify(agent, f"New pickup assigned: '{item.title}' from {item.uploaded_by.username}. Restoration Engineer: {item.assigned_mechanic.username if item.assigned_mechanic else 'To be assigned'}")
        notify(item.uploaded_by, f"Agent {agent.username} will collect your item '{item.title}'.")
        log(request.user, f"Assigned agent {agent.username} (and mechanic) to collect: {item.title}")
        messages.success(request, f"logistics protocol initiated for '{item.title}'. Agent {agent.username} is dispatched.")
        return redirect('admin_dashboard')
        
    return render(request, 'core/admin_assign_agent.html', {
        'item': item, 
        'agents': agents, 
        'mechanics': mechanics
    })

@login_required
@user_passes_test(is_admin)
def admin_assign_mechanic(request, pk):
    item = get_object_or_404(EWasteItem, pk=pk, status='collected')
    mechanics = CustomUser.objects.filter(role='MECHANIC', mechanic_profile__verification_status='Approved')
    if request.method == 'POST':
        mechanic_id = request.POST.get('mechanic_id')
        mechanic = get_object_or_404(CustomUser, pk=mechanic_id, role='MECHANIC')
        item.assigned_mechanic = mechanic
        item.status = 'mechanic_assigned'
        item.save()
        notify(mechanic, f"New repair job: '{item.title}' by {item.uploaded_by.username}.")
        notify(item.uploaded_by, f"Mechanic {mechanic.username} is repairing your item '{item.title}'.")
        log(request.user, f"Assigned mechanic {mechanic.username} to repair: {item.title}")
        messages.success(request, f"Mechanic {mechanic.username} assigned to repair '{item.title}'.")
        return redirect('admin_dashboard')
    return render(request, 'core/admin_assign_mechanic.html', {'item': item, 'mechanics': mechanics})

@login_required
@user_passes_test(is_admin)
def admin_assign_retrieval_agent(request, pk):
    item = get_object_or_404(EWasteItem, pk=pk, status='repair_completed')
    agents = CustomUser.objects.filter(role='AGENT', agent_profile__verification_status='Approved')
    
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id')
        agent = get_object_or_404(CustomUser, pk=agent_id, role='AGENT')
        item.assigned_agent = agent
        item.status = 'repair_completed' # Keep as completed but with assigned agent
        item.save()
        
        notify(agent, f"Retrieval duty: Pick up restored unit '{item.title}' from Mechanic @{item.assigned_mechanic.username}.")
        notify(item.assigned_mechanic, f"Agent {agent.username} is dispatched for retrieval of '{item.title}'.")
        log(request.user, f"Assigned agent {agent.username} to retrieve finished unit: {item.title}")
        messages.success(request, f"Retrieval signal sent to Agent {agent.username}.")
        return redirect('admin_dashboard')
        
    return render(request, 'core/admin_assign_agent.html', {
        'item': item, 
        'agents': agents,
        'is_retrieval': True
    })

@login_required
@user_passes_test(is_admin)
def admin_publish_product(request, pk):
    # Allow injection from both Central Hub and directly from Mechanic Nodes
    item = get_object_or_404(EWasteItem, pk=pk, status__in=['repair_completed', 'awaiting_admin_approval'])
    
    # Get repair log to determine price
    repair_log = getattr(item, 'repair_log', None)
    repair_cost = float(repair_log.cost) if repair_log else 0
    
    product, created = Product.objects.get_or_create(
        linked_item=item,
        defaults={
            'price':       round(repair_cost * 1.5, 2),
            'image':       item.image,
            'description': f"Certified Restoration: {item.title} — Verified for deployment.",
            'is_published': True,
        }
    )
    
    if not created:
        product.is_published = True
        product.save()
        
    item.status = 'published_in_store'
    item.published_at = timezone.now()
    item.save()
    
    notify(item.uploaded_by, f"Cycle Complete: Your item '{item.title}' has been restored and is now featured in the hub store!")
    log(request.user, f"Injected product into store: {item.title}")
    messages.success(request, f"'{item.title}' successfully injected into the market inventory.")
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def admin_assign_delivery_agent(request, pk):
    order = get_object_or_404(Order, pk=pk, status='ordered')
    agents = CustomUser.objects.filter(role='AGENT', agent_profile__verification_status='Approved')
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id')
        agent = get_object_or_404(CustomUser, pk=agent_id, role='AGENT')
        order.assigned_agent = agent
        order.status = 'delivery_assigned'
        order.save()
        notify(agent, f"New Asset Deployment: Order #{order.id} assigned. Prepare for pickup.")
        notify(order.buyer, f"Your order #{order.id} has been assigned to Logistics Agent {agent.username}.")
        log(request.user, f"Assigned delivery agent {agent.username} to Order #{order.id}")
        messages.success(request, f"Delivery agent assigned to Order #{order.id}.")
        return redirect('orders')
    return render(request, 'core/admin_assign_agent.html', {'order': order, 'agents': agents, 'is_delivery': True})

@login_required
@user_passes_test(is_agent, login_url='/login/agent/')
def agent_dispatch_order(request, pk):
    order = get_object_or_404(Order, pk=pk, assigned_agent=request.user)
    action = request.POST.get('action')
    
    if action == 'pickup':
        order.status = 'delivery_assigned' # Stay in assigned but maybe update a sub-status if we had one
        msg = "Asset secured at Logistic Node."
    elif action == 'out_for_delivery':
        order.status = 'out_for_delivery'
        msg = "Asset is now in tactical transit (Last Mile)."
    else:
        return redirect('agent_dashboard')
        
    order.save()
    notify(order.buyer, f"Logistics Update: Order #{order.id} - {msg}")
    log(request.user, f"Transitioned Order #{order.id} to {order.status}")
    messages.success(request, f"Order status updated: {order.status}")
    return redirect('agent_dashboard')

# Admin management pages

@login_required
@user_passes_test(is_admin)
def admin_manage_users(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    context = {
        'users':           users,
        'total_customers': CustomUser.objects.filter(role='CUSTOMER').count(),
        'total_agents':    CustomUser.objects.filter(role='AGENT').count(),
        'total_mechanics': CustomUser.objects.filter(role='MECHANIC').count(),
    }
    return render(request, 'core/dashboard/admin/admin_manage_users.html', context)

@login_required
@user_passes_test(is_admin)
def admin_user_detail(request, pk):
    member = get_object_or_404(CustomUser, pk=pk)
    profile = None
    assigned_tasks = []
    performance_metrics = {}

    if member.role == 'AGENT':
        profile = getattr(member, 'agent_profile', None)
        # Combine pickups and deliveries for a unified report
        pickups = member.agent_pickups.all()
        deliveries = member.delivery_orders.all()
        assigned_tasks = list(pickups) + list(deliveries)
        performance_metrics = {
            'Total Tasks': len(assigned_tasks),
            'Completed Collections': pickups.filter(status='collected').count(),
            'Active Deliveries': deliveries.filter(status='out_for_delivery').count(),
            'Successful Deliveries': deliveries.filter(status='delivered').count(),
        }
    elif member.role == 'MECHANIC':
        profile = getattr(member, 'mechanic_profile', None)
        jobs = member.mechanic_jobs.all()
        assigned_tasks = jobs
        performance_metrics = {
            'Total Jobs': jobs.count(),
            'In Restoration': jobs.filter(status='mechanic_assigned').count(),
            'Successfully Repaired': jobs.filter(status='repair_completed').count(),
        }
    elif member.role == 'CUSTOMER':
        profile = getattr(member, 'customer_profile', None)
        uploads = member.uploaded_items.all()
        orders = member.my_orders.all()
        assigned_tasks = list(uploads) + list(orders)
        performance_metrics = {
            'Assets Uploaded': uploads.count(),
            'Orders Placed': orders.count(),
            'Total Value Contributed': sum(p.price for p in Product.objects.filter(linked_item__in=uploads, is_published=True)),
        }

    return render(request, 'core/dashboard/admin/admin_user_detail.html', {
        'member': member,
        'profile': profile,
        'assigned_tasks': assigned_tasks,
        'metrics': performance_metrics,
    })


@login_required
@user_passes_test(is_admin)
def admin_delete_user(request, pk):
    user_obj = get_object_or_404(CustomUser, pk=pk)
    if user_obj.role != 'ADMIN':
        username = user_obj.username
        user_obj.delete()
        log(request.user, f"Deleted user: {username}")
        messages.success(request, f"User '{username}' deleted.")
    else:
        messages.error(request, "Cannot delete Admin accounts.")
    return redirect('manage_users')

@login_required
@user_passes_test(is_admin)
def admin_toggle_user_status(request, pk):
    user_obj = get_object_or_404(CustomUser, pk=pk)
    if user_obj.role == 'ADMIN':
        messages.error(request, "Admin status cannot be modified.")
    else:
        user_obj.is_active = not user_obj.is_active
        user_obj.save()
        status = "Activated" if user_obj.is_active else "Suspended"
        log(request.user, f"{status} user: {user_obj.username}")
        messages.success(request, f"User '{user_obj.username}' has been {status.lower()}.")
    return redirect('user_detail', pk=pk)

@login_required
@user_passes_test(is_admin)
def admin_revoke_credentials(request, pk):
    user_obj = get_object_or_404(CustomUser, pk=pk)
    profile = None
    if user_obj.role == 'AGENT':
        profile = getattr(user_obj, 'agent_profile', None)
    elif user_obj.role == 'MECHANIC':
        profile = getattr(user_obj, 'mechanic_profile', None)
    
    if profile:
        profile.verification_status = 'Rejected'
        profile.save()
        log(request.user, f"Revoked credentials for: {user_obj.username}")
        notify(user_obj, "Your professional credentials have been revoked by Admin Audit. Please contact support.")
        messages.warning(request, f"Credentials revoked for '{user_obj.username}'.")
    else:
        messages.error(request, "This user role does not have revocable professional credentials.")
    return redirect('user_detail', pk=pk)

@login_required
@user_passes_test(is_admin)
def admin_approve_profile(request, pk, role):
    if role == 'agent':
        profile = get_object_or_404(AgentProfile, user__pk=pk)
    else:
        profile = get_object_or_404(MechanicProfile, user__pk=pk)

    action = request.POST.get('action', 'approve')
    if action == 'approve':
        profile.verification_status = 'Approved'
        notify(profile.user, f"Your {role} account has been verified and approved!")
        log(request.user, f"Approved {role}: {profile.user.username}")
        messages.success(request, f"{role.title()} {profile.user.username} approved.")
    else:
        profile.verification_status = 'Rejected'
        notify(profile.user, f"Your {role} application was not approved. Contact support.")
        log(request.user, f"Rejected {role}: {profile.user.username}")
        messages.warning(request, f"{role.title()} {profile.user.username} rejected.")
    profile.save()
    return redirect('manage_users')

@login_required
@user_passes_test(is_admin)
def admin_manage_products(request):
    items = EWasteItem.objects.all()
    return render(request, 'core/dashboard/admin/admin_manage_products.html', {'items': items})

@login_required
@user_passes_test(is_admin)
def admin_published_products(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'core/dashboard/admin/admin_published_products.html', {'products': products})

@login_required
@user_passes_test(is_admin)
def admin_item_detail(request, pk):
    item = get_object_or_404(EWasteItem, pk=pk)
    # Check if this item has been converted to a product
    product = getattr(item, 'product', None)
    orders = []
    if product:
        # Get all orders associated with the product deployment
        orders = Order.objects.filter(product=product).order_by('-created_at')
    
    return render(request, 'core/dashboard/admin/admin_item_detail.html', {
        'item': item,
        'product': product,
        'orders': orders,
    })

@login_required
@user_passes_test(is_admin)
def admin_orders(request):
    all_orders = Order.objects.all().order_by('-created_at')
    return render(request, 'core/dashboard/admin/admin_orders.html', {'orders': all_orders})

@login_required
@user_passes_test(is_admin)
def admin_mechanic_payments(request):
    logs = RepairLog.objects.all().order_by('-completed_at')
    pending_payouts = logs.filter(is_paid=False)
    paid_payouts = logs.filter(is_paid=True)
    
    total_pending = pending_payouts.aggregate(total=Sum('cost'))['total'] or 0
    
    return render(request, 'core/dashboard/admin/admin_mechanic_payments.html', {
        'logs': logs,
        'pending_payouts': pending_payouts,
        'paid_payouts': paid_payouts,
        'total_pending': total_pending
    })

@login_required
@user_passes_test(is_admin)
def admin_pay_mechanic(request, pk):
    log_entry = get_object_or_404(RepairLog, pk=pk)
    if request.method == 'POST':
        ref = request.POST.get('reference')
        log_entry.is_paid = True
        log_entry.paid_at = timezone.now()
        log_entry.payment_reference = ref
        log_entry.save()
        
        log(request.user, f"Payment Dispersed: ₹{log_entry.cost} to Mechanic @{log_entry.mechanic.username} for Asset #{log_entry.item.id}")
        notify(log_entry.mechanic, f"Payment Verification: ₹{log_entry.cost} has been credited for your restoration of '{log_entry.item.title}'. Ref: {ref}")
        messages.success(request, f"Payout mission successful. Mechanic @{log_entry.mechanic.username} notified.")
        
    return redirect('admin_mechanic_payments')


@login_required
@user_passes_test(is_admin)
def admin_activity_logs(request):
    logs_list = ActivityLog.objects.all().order_by('-timestamp')
    paginator = Paginator(logs_list, 20)
    page_number = request.GET.get('page')
    logs = paginator.get_page(page_number)
    return render(request, 'core/dashboard/admin/admin_activity_logs.html', {'logs': logs})

@login_required
@user_passes_test(is_admin)
def admin_analytics(request):
    """Deep analytics for enterprise performance monitoring."""
    from django.db.models import Count, Sum
    from datetime import timedelta
    from django.utils import timezone
    import json
    
    # Revenue by Category
    category_data_qs = Product.objects.values('linked_item__category').annotate(revenue=Sum('price')).order_by('-revenue')
    category_labels = [item['linked_item__category'] for item in category_data_qs]
    category_values = [float(item['revenue']) for item in category_data_qs]
    
    # Orders over last 30 days
    from django.db.models.functions import TruncDay
    last_30_days = timezone.now() - timedelta(days=30)
    orders_trend_qs = Order.objects.filter(created_at__gte=last_30_days).annotate(day=TruncDay('created_at')).values('day').annotate(count=Count('id')).order_by('day')
    trend_labels = [item['day'].strftime('%Y-%m-%d') for item in orders_trend_qs]
    trend_values = [item['count'] for item in orders_trend_qs]
    
    context = {
        'category_labels': json.dumps(category_labels),
        'category_values': json.dumps(category_values),
        'trend_labels': json.dumps(trend_labels),
        'trend_values': json.dumps(trend_values),
        'total_revenue': Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0,
        'avg_repair_cost': RepairLog.objects.aggregate(Sum('cost'))['cost__sum'] or 0,
    }
    return render(request, 'core/dashboard/admin/admin_analytics.html', context)

@login_required
@user_passes_test(is_admin)
def export_inventory_csv(request):
    """Export the entire asset inventory to CSV for executive reporting."""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="efixhub_inventory_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Title', 'Category', 'Status', 'Uploader', 'Mechanic', 'Progress', 'Created At'])
    
    for item in EWasteItem.objects.all().select_related('uploaded_by', 'assigned_mechanic'):
        writer.writerow([
            item.id,
            item.title,
            item.get_category_display(),
            item.get_status_display(),
            item.uploaded_by.username,
            item.assigned_mechanic.username if item.assigned_mechanic else 'N/A',
            f"{item.repair_progress_percentage}%",
            item.created_at.strftime("%Y-%m-%d %H:%M")
        ])
        
    return response


# ═══════════════════════════════════════════════════════════════════
# SHARED / STORE VIEWS
# ═══════════════════════════════════════════════════════════════════

def browse_store(request):
    category = request.GET.get('category')
    products = Product.objects.filter(is_published=True, is_sold=False)
    
    if category:
        products = products.filter(linked_item__category=category)
    
    # Get all categories for filter buttons
    categories = EWasteItem.CATEGORY_CHOICES
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category
    }
    return render(request, 'core/refurbished_store.html', context)

@login_required
def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk, is_published=True)
    return render(request, 'core/product_detail_view.html', {'product': product})
