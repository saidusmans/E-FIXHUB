from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator


# ═══════════════════════════════════════════════════════════════════
# CUSTOM USER MODEL
# ═══════════════════════════════════════════════════════════════════

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN',    'Administrator'),
        ('CUSTOMER', 'Customer'),
        ('AGENT',    'Field Agent'),
        ('MECHANIC', 'Restoration Engineer'),
    )
    email    = models.EmailField(unique=True)
    role     = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CUSTOMER')
    phone    = models.CharField(max_length=15, blank=True, null=True)
    state    = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    address  = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_verified(self):
        if self.role == 'ADMIN' or self.is_superuser:
            return True
        if self.role == 'AGENT':
            return getattr(self, 'agent_profile', None) and self.agent_profile.verification_status == 'Approved'
        if self.role == 'MECHANIC':
            return getattr(self, 'mechanic_profile', None) and self.mechanic_profile.verification_status == 'Approved'
        if self.role == 'CUSTOMER':
            return True # Customers are verified by default upon registration
        return False


# ═══════════════════════════════════════════════════════════════════
# ROLE PROFILES
# ═══════════════════════════════════════════════════════════════════

class CustomerProfile(models.Model):
    user    = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='customer_profile')
    name    = models.CharField(max_length=255, blank=True, null=True) # Full Name
    phone   = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Customer: {self.user.username}"


class AgentProfile(models.Model):
    VERIFICATION_STATUS = (
        ('Pending',  'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    user                = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='agent_profile')
    name                = models.CharField(max_length=255, blank=True, null=True)
    phone               = models.CharField(max_length=15, blank=True, null=True)
    location            = models.CharField(max_length=255, blank=True, null=True)
    operation_zone      = models.CharField(max_length=255, blank=True, null=True, help_text="Primary district of operation")
    vehicle_details     = models.CharField(max_length=255, blank=True, null=True)
    qualification       = models.CharField(max_length=255, blank=True, null=True)
    experience          = models.PositiveIntegerField(default=0)
    id_proof_upload     = models.FileField(upload_to='id_proofs/agents/', blank=True, null=True, validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])])
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='Pending')
    is_available        = models.BooleanField(default=True)

    def __str__(self):
        return f"Agent: {self.user.username} [{self.verification_status}]"


class MechanicProfile(models.Model):
    VERIFICATION_STATUS = (
        ('Pending',  'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    user                = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='mechanic_profile')
    name                = models.CharField(max_length=255, blank=True, null=True)
    phone               = models.CharField(max_length=15, blank=True, null=True)
    experience          = models.PositiveIntegerField(default=0)
    location            = models.CharField(max_length=255, blank=True, null=True)
    specialization      = models.CharField(max_length=255, blank=True, null=True)
    qualification       = models.CharField(max_length=255, blank=True, null=True)
    workshop_address    = models.TextField(blank=True, null=True)
    workstation_images = models.ImageField(upload_to='workshops/', blank=True, null=True)
    id_proof_upload     = models.FileField(upload_to='id_proofs/mechanics/', blank=True, null=True, validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])])
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='Pending')

    def __str__(self):
        return f"Mechanic: {self.user.username} [{self.verification_status}]"


# ═══════════════════════════════════════════════════════════════════
# E-WASTE ITEM (CHAIN OF CUSTODY)
# ═══════════════════════════════════════════════════════════════════

class EWasteItem(models.Model):
    STATUS_CHOICES = (
        ('uploaded',                 'Uploaded'),
        ('inspection_pending',       'Inspection Pending'),
        ('agent_assigned',           'Agent Assigned'),
        ('collected',                'Collected'),
        ('mechanic_assigned',        'Mechanic Assigned'),
        ('repairing',                'Repairing'),
        ('repair_completed',         'Repair Completed'),
        ('awaiting_admin_approval',  'Awaiting Admin Approval'),
        ('published_in_store',       'Published in Store'),
        ('ordered',                  'Ordered'),
        ('delivery_assigned',        'Delivery Assigned'),
        ('delivered',                'Delivered'),
    )
    CATEGORY_CHOICES = (
        ('Mobile',    'Mobile Phone'),
        ('Laptop',    'Laptop / Computer'),
        ('TV',        'Television'),
        ('Appliance', 'Home Appliance'),
        ('Other',     'Other Electronics'),
    )
    uploaded_by       = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='uploaded_items')
    title             = models.CharField(max_length=255)
    category          = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    description       = models.TextField()
    condition         = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Broken screen, No power")
    image             = models.ImageField(upload_to='ewaste/')
    status            = models.CharField(max_length=40, choices=STATUS_CHOICES, default='uploaded')
    repair_progress_percentage = models.PositiveIntegerField(default=0, help_text="Completion percentage (0-100)")

    # Real DB fields added in migration 0006
    parts_replaced            = models.TextField(blank=True, null=True, help_text="List of components replaced during restoration")
    estimated_completion_date = models.DateField(blank=True, null=True)

    # Collection Location (migration 0003)
    collection_district = models.CharField(max_length=100, blank=True, null=True, help_text="District for pickup")
    collection_address  = models.TextField(blank=True, null=True, help_text="Full address for agent to collect from")

    assigned_agent    = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='agent_pickups')
    assigned_mechanic = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='mechanic_jobs')

    @property
    def overall_progress(self):
        mapping = {
            'uploaded': 10,
            'inspection_pending': 20,
            'agent_assigned': 30,
            'collected': 40,
            'mechanic_assigned': 50,
            'repairing': 70,
            'repair_completed': 85,
            'awaiting_admin_approval': 90,
            'published_in_store': 100,
            'ordered': 100,
            'delivery_assigned': 100,
            'delivered': 100,
            'cancelled': 0
        }
        return mapping.get(self.status, 5)

    # Lifecycle Timestamps
    created_at   = models.DateTimeField(auto_now_add=True)
    approved_at  = models.DateTimeField(blank=True, null=True)
    collected_at = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    restored_at  = models.DateTimeField(blank=True, null=True)
    sold_at      = models.DateTimeField(blank=True, null=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} [{self.status}]"

    # ── Backward-compat aliases so views/templates keep working ──
    @property
    def user(self):
        return self.uploaded_by

    @property
    def restoration_progress(self):
        """Alias for repair_progress_percentage."""
        return self.repair_progress_percentage

    @property
    def repair_notes(self):
        """Alias for parts_replaced for template/view backward compat."""
        return self.parts_replaced

    @repair_notes.setter
    def repair_notes(self, value):
        self.parts_replaced = value

    class Meta:
        ordering = ['-created_at']


# ═══════════════════════════════════════════════════════════════════
# REPAIR LOG
# ═══════════════════════════════════════════════════════════════════

class RepairLog(models.Model):
    item              = models.OneToOneField(EWasteItem, on_delete=models.CASCADE, related_name='repair_log')
    mechanic          = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='repairs_done')
    repair_notes      = models.TextField()
    cost              = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount to be paid to mechanic")
    is_paid           = models.BooleanField(default=False)
    paid_at           = models.DateTimeField(blank=True, null=True)
    payment_reference = models.CharField(max_length=255, blank=True, null=True, help_text="Transaction ID or Receipt No.")
    completed_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Repair of '{self.item.title}' by {self.mechanic.username} — {'PAID' if self.is_paid else 'PENDING'}"


# ═══════════════════════════════════════════════════════════════════
# PRODUCT (AUTO-CREATED FROM REPAIR)
# ═══════════════════════════════════════════════════════════════════

class Product(models.Model):
    STORE_STATUS_CHOICES = (
        ('Draft',        'Draft'),
        ('Published',    'Published'),
        ('Out of Stock', 'Out of Stock'),
        ('Sold',         'Sold'),
    )
    linked_item  = models.OneToOneField(EWasteItem, on_delete=models.CASCADE, related_name='product')
    price        = models.DecimalField(max_digits=10, decimal_places=2)
    image        = models.ImageField(upload_to='products/', blank=True, null=True)
    description  = models.TextField(blank=True, null=True)
    stock        = models.PositiveIntegerField(default=1)
    is_published = models.BooleanField(default=False)
    is_sold      = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    @property
    def display_image(self):
        """Return product image or fall back to linked e-waste item image."""
        if self.image:
            return self.image
        return self.linked_item.image

    def __str__(self):
        return f"Product: {self.linked_item.title} — ₹{self.price}"


# ═══════════════════════════════════════════════════════════════════
# ORDER
# ═══════════════════════════════════════════════════════════════════

class Order(models.Model):
    STATUS_CHOICES = (
        ('ordered',           'Ordered'),
        ('delivery_assigned',  'Delivery Assigned'),
        ('out_for_delivery',  'Out for Delivery'),
        ('delivered',         'Delivered'),
        ('cancelled',         'Cancelled'),
    )
    PAYMENT_CHOICES = (
        ('COD', 'Cash on Delivery'),
        ('Online', 'Online Payment'),
    )
    product        = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    buyer          = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='my_orders')
    assigned_agent = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='delivery_orders')
    total_price    = models.DecimalField(max_digits=10, decimal_places=2)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ordered')
    payment_method   = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='COD')
    shipping_name    = models.CharField(max_length=255, blank=True, null=True)
    shipping_phone   = models.CharField(max_length=15, blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} — {self.product.linked_item.title} → {self.buyer.username}"


# ═══════════════════════════════════════════════════════════════════
# NOTIFICATION
# ═══════════════════════════════════════════════════════════════════

class Notification(models.Model):
    user       = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{'Read' if self.is_read else 'Unread'}] {self.user.username}: {self.message[:40]}"

    class Meta:
        ordering = ['-created_at']


# ═══════════════════════════════════════════════════════════════════
# ACTIVITY LOG
# ═══════════════════════════════════════════════════════════════════

class ActivityLog(models.Model):
    user      = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activity_logs')
    action    = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"@{self.user.username}: {self.action}"

    class Meta:
        ordering = ['-timestamp']


# ═══════════════════════════════════════════════════════════════════
# GALLERY (FOR HOME PAGE)
# ═══════════════════════════════════════════════════════════════════

class Gallery(models.Model):
    title       = models.CharField(max_length=255)
    image       = models.ImageField(upload_to='gallery/')
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
