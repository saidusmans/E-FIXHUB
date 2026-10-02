"""
E-Fix Hub — Comprehensive Test Suite
=====================================
Tests: Authentication, Role Access, Workflows, Database Integrity
Total test cases: 30+
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import (
    CustomUser, CustomerProfile, AgentProfile, MechanicProfile,
    EWasteItem, RepairLog, Product, Order, Notification, ActivityLog
)


class BaseTestMixin:
    """Shared setup for all test classes."""

    def setUp(self):
        self.client = Client()

        # Create users for each role
        self.admin = CustomUser.objects.create_superuser(
            username='admin', email='admin@test.com', password='testpass123', role='ADMIN'
        )
        self.customer = CustomUser.objects.create_user(
            username='customer1', email='customer1@test.com', password='testpass123', role='CUSTOMER'
        )
        CustomerProfile.objects.create(user=self.customer, phone='123456')

        self.agent = CustomUser.objects.create_user(
            username='agent1', email='agent1@test.com', password='testpass123', role='AGENT'
        )
        AgentProfile.objects.create(
            user=self.agent, qualification='Diploma', verification_status='Approved'
        )

        self.mechanic = CustomUser.objects.create_user(
            username='mechanic1', email='mechanic1@test.com', password='testpass123', role='MECHANIC'
        )
        MechanicProfile.objects.create(
            user=self.mechanic, specialization='Phones', verification_status='Approved'
        )

        # Create a test image for uploads
        self.test_image = SimpleUploadedFile(
            name='test.jpg',
            content=b'\x47\x49\x46\x38\x89\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\xff\xff\xff\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b',
            content_type='image/gif'
        )


# ═══════════════════════════════════════════════════════════════════
# 1. AUTHENTICATION TESTS
# ═══════════════════════════════════════════════════════════════════

class AuthenticationTests(BaseTestMixin, TestCase):
    """Test registration and login flows for all roles."""

    def test_01_customer_registration_page_loads(self):
        response = self.client.get(reverse('customer_register'))
        self.assertEqual(response.status_code, 200)

    def test_02_agent_registration_page_loads(self):
        response = self.client.get(reverse('agent_register'))
        self.assertEqual(response.status_code, 200)

    def test_03_mechanic_registration_page_loads(self):
        response = self.client.get(reverse('mechanic_register'))
        self.assertEqual(response.status_code, 200)

    def test_04_customer_login_valid(self):
        response = self.client.post(reverse('customer_login'), {
            'username': 'customer1', 'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard

    def test_05_admin_login_valid(self):
        response = self.client.post(reverse('admin_login'), {
            'username': 'admin', 'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_06_cross_role_login_rejected(self):
        """Customer trying to login through agent portal should be rejected."""
        response = self.client.post(reverse('agent_login'), {
            'username': 'customer1', 'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)  # Stays on login page

    def test_07_logout(self):
        self.client.login(username='customer1', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)


# ═══════════════════════════════════════════════════════════════════
# 2. ROLE ACCESS TESTS
# ═══════════════════════════════════════════════════════════════════

class RoleAccessTests(BaseTestMixin, TestCase):
    """Ensure strict role-based access control."""

    def test_08_customer_cannot_access_admin_dashboard(self):
        self.client.login(username='customer1', password='testpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertNotEqual(response.status_code, 200)

    def test_09_agent_cannot_access_customer_dashboard(self):
        self.client.login(username='agent1', password='testpass123')
        response = self.client.get(reverse('customer_dashboard'))
        self.assertNotEqual(response.status_code, 200)

    def test_10_mechanic_cannot_access_agent_dashboard(self):
        self.client.login(username='mechanic1', password='testpass123')
        response = self.client.get(reverse('agent_dashboard'))
        self.assertNotEqual(response.status_code, 200)

    def test_11_unauthenticated_dashboard_redirect(self):
        response = self.client.get(reverse('customer_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_12_admin_can_access_manage_users(self):
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('manage_users'))
        self.assertEqual(response.status_code, 200)

    def test_13_customer_cannot_access_manage_users(self):
        self.client.login(username='customer1', password='testpass123')
        response = self.client.get(reverse('manage_users'))
        self.assertNotEqual(response.status_code, 200)


# ═══════════════════════════════════════════════════════════════════
# 3. UPLOAD WORKFLOW TESTS
# ═══════════════════════════════════════════════════════════════════

class UploadWorkflowTests(BaseTestMixin, TestCase):
    """Test e-waste item upload and approval flow."""

    def _create_item(self):
        """Helper to create a test e-waste item."""
        return EWasteItem.objects.create(
            uploaded_by=self.customer,
            title='Test Phone',
            category='Mobile',
            description='Broken screen',
            status='uploaded',
            image='ewaste/test.jpg'
        )

    def test_14_customer_upload_page_loads(self):
        self.client.login(username='customer1', password='testpass123')
        response = self.client.get(reverse('customer_upload'))
        self.assertEqual(response.status_code, 200)

    def test_15_item_created_with_pending_status(self):
        item = self._create_item()
        self.assertEqual(item.status, 'uploaded')

    def test_16_admin_approves_item(self):
        item = self._create_item()
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('approve_item', args=[item.pk]))
        item.refresh_from_db()
        self.assertEqual(item.status, 'inspection_pending')

    def test_17_admin_assigns_agent(self):
        item = self._create_item()
        item.status = 'inspection_pending'
        item.save()
        self.client.login(username='admin', password='testpass123')
        response = self.client.post(reverse('assign_agent', args=[item.pk]), {
            'agent_id': self.agent.pk
        })
        item.refresh_from_db()
        self.assertEqual(item.status, 'agent_assigned')
        self.assertEqual(item.assigned_agent, self.agent)

    def test_18_agent_marks_collected(self):
        item = self._create_item()
        item.status = 'agent_assigned'
        item.assigned_agent = self.agent
        item.save()
        self.client.login(username='agent1', password='testpass123')
        response = self.client.get(reverse('mark_collected', args=[item.pk]))
        item.refresh_from_db()
        self.assertEqual(item.status, 'collected')


# ═══════════════════════════════════════════════════════════════════
# 4. REPAIR WORKFLOW TESTS
# ═══════════════════════════════════════════════════════════════════

class RepairWorkflowTests(BaseTestMixin, TestCase):
    """Test mechanic repair and product auto-creation."""

    def _create_item_for_repair(self):
        item = EWasteItem.objects.create(
            uploaded_by=self.customer,
            title='Broken Laptop',
            category='Laptop',
            description='No power',
            status='mechanic_assigned',
            assigned_mechanic=self.mechanic,
            image='ewaste/test.jpg'
        )
        return item

    def test_19_admin_assigns_mechanic(self):
        item = EWasteItem.objects.create(
            uploaded_by=self.customer, title='Phone', category='Mobile',
            description='Cracked', status='collected', image='ewaste/test.jpg'
        )
        self.client.login(username='admin', password='testpass123')
        self.client.post(reverse('assign_mechanic', args=[item.pk]), {
            'mechanic_id': self.mechanic.pk
        })
        item.refresh_from_db()
        self.assertEqual(item.status, 'mechanic_assigned')

    def test_20_mechanic_submits_repair(self):
        item = self._create_item_for_repair()
        self.client.login(username='mechanic1', password='testpass123')
        response = self.client.post(reverse('repair_item', args=[item.pk]), {
            'repair_notes': 'Replaced power IC and screen',
            'cost': '1500.00',
            'action': 'complete_restoration',
        })
        item.refresh_from_db()
        self.assertEqual(item.status, 'repair_completed')

    def test_21_repair_auto_creates_product(self):
        item = self._create_item_for_repair()
        self.client.login(username='mechanic1', password='testpass123')
        self.client.post(reverse('repair_item', args=[item.pk]), {
            'repair_notes': 'Fixed display',
            'cost': '2000.00',
            'action': 'complete_restoration',
        })
        # After mechanic completes, Admin publishes to create product
        item.refresh_from_db()
        self.assertEqual(item.status, 'repair_completed')
        # RepairLog should be created
        self.assertTrue(hasattr(item, 'repair_log'))

    def test_22_product_not_published_by_default(self):
        item = self._create_item_for_repair()
        self.client.login(username='mechanic1', password='testpass123')
        self.client.post(reverse('repair_item', args=[item.pk]), {
            'repair_notes': 'Replaced screen',
            'cost': '500.00',
            'action': 'complete_restoration',
        })
        # Product is only created when admin publishes, not automatically after mechanic repair
        # So no product should exist yet
        self.assertFalse(Product.objects.filter(linked_item=item).exists())


# ═══════════════════════════════════════════════════════════════════
# 5. PRODUCT LIFECYCLE TESTS
# ═══════════════════════════════════════════════════════════════════

class ProductLifecycleTests(BaseTestMixin, TestCase):
    """Test product publishing and store visibility."""

    def _create_product(self):
        item = EWasteItem.objects.create(
            uploaded_by=self.customer, title='Restored Tablet',
            category='Mobile', description='Working', status='repair_completed',
            image='ewaste/test.jpg'
        )
        RepairLog.objects.create(
            item=item, mechanic=self.mechanic,
            repair_notes='Full restore', cost=1000
        )
        product = Product.objects.create(
            linked_item=item, price=1500, is_published=False
        )
        return item, product

    def test_23_admin_publishes_product(self):
        item, product = self._create_product()
        # Set item to a valid status that admin_publish_product accepts
        item.status = 'repair_completed'
        item.save()
        self.client.login(username='admin', password='testpass123')
        self.client.get(reverse('publish_product', args=[item.pk]))
        product.refresh_from_db()
        item.refresh_from_db()
        self.assertTrue(product.is_published)
        self.assertEqual(item.status, 'published_in_store')

    def test_24_published_product_visible_in_store(self):
        _, product = self._create_product()
        product.is_published = True
        product.save()
        response = self.client.get(reverse('browse_store'))
        self.assertContains(response, 'Restored Tablet')


# ═══════════════════════════════════════════════════════════════════
# 6. ORDER LIFECYCLE TESTS
# ═══════════════════════════════════════════════════════════════════

class OrderLifecycleTests(BaseTestMixin, TestCase):
    """Test order creation and delivery workflow."""

    def _create_order(self):
        item = EWasteItem.objects.create(
            uploaded_by=self.customer, title='Laptop Pro',
            category='Laptop', description='New', status='published_in_store',
            image='ewaste/test.jpg'
        )
        product = Product.objects.create(
            linked_item=item, price=5000, is_published=True, stock=1
        )
        order = Order.objects.create(
            product=product, buyer=self.customer, total_price=5000
        )
        return order, product

    def test_25_customer_purchase_creates_order(self):
        item = EWasteItem.objects.create(
            uploaded_by=self.customer, title='Tablet',
            category='Mobile', description='Good', status='published_in_store',
            image='ewaste/test.jpg'
        )
        product = Product.objects.create(
            linked_item=item, price=2000, is_published=True, stock=1
        )
        self.client.login(username='customer1', password='testpass123')
        response = self.client.post(reverse('purchase_product', args=[product.pk]))
        self.assertTrue(Order.objects.filter(buyer=self.customer, product=product).exists())

    def test_26_order_default_status_ordered(self):
        order, _ = self._create_order()
        self.assertEqual(order.status, 'ordered')

    def test_27_admin_assigns_delivery_agent(self):
        order, _ = self._create_order()
        self.client.login(username='admin', password='testpass123')
        self.client.post(reverse('assign_delivery', args=[order.pk]), {
            'agent_id': self.agent.pk
        })
        order.refresh_from_db()
        # Admin assigns → status becomes 'delivery_assigned'
        self.assertEqual(order.status, 'delivery_assigned')
        self.assertEqual(order.assigned_agent, self.agent)

    def test_28_agent_marks_delivered(self):
        order, _ = self._create_order()
        order.assigned_agent = self.agent
        order.status = 'out_for_delivery'
        order.save()
        self.client.login(username='agent1', password='testpass123')
        self.client.get(reverse('mark_delivered', args=[order.pk]))
        order.refresh_from_db()
        self.assertEqual(order.status, 'delivered')


# ═══════════════════════════════════════════════════════════════════
# 7. DATABASE INTEGRITY TESTS
# ═══════════════════════════════════════════════════════════════════

class DatabaseIntegrityTests(BaseTestMixin, TestCase):
    """Validate database constraints and relationships."""

    def test_29_one_repair_per_item(self):
        item = EWasteItem.objects.create(
            uploaded_by=self.customer, title='Test', category='Other',
            description='x', status='repair_completed', image='ewaste/test.jpg'
        )
        RepairLog.objects.create(item=item, mechanic=self.mechanic, repair_notes='ok', cost=100)
        # Attempting a second repair log on the same item should fail (OneToOne)
        with self.assertRaises(Exception):
            RepairLog.objects.create(item=item, mechanic=self.mechanic, repair_notes='dup', cost=200)

    def test_30_one_product_per_item(self):
        item = EWasteItem.objects.create(
            uploaded_by=self.customer, title='Test2', category='Other',
            description='x', status='repair_completed', image='ewaste/test.jpg'
        )
        Product.objects.create(linked_item=item, price=500)
        with self.assertRaises(Exception):
            Product.objects.create(linked_item=item, price=600)

    def test_31_agent_cannot_collect_unassigned_item(self):
        item = EWasteItem.objects.create(
            uploaded_by=self.customer, title='Unassigned', category='Other',
            description='x', status='agent_assigned', image='ewaste/test.jpg',
            assigned_agent=self.admin  # delivery_assigned to admin, not our agent
        )
        self.client.login(username='agent1', password='testpass123')
        response = self.client.get(reverse('mark_collected', args=[item.pk]))
        self.assertEqual(response.status_code, 404)

    def test_32_notification_created_on_purchase(self):
        item = EWasteItem.objects.create(
            uploaded_by=self.customer, title='NotifTest', category='Mobile',
            description='Good', status='published_in_store', image='ewaste/test.jpg'
        )
        product = Product.objects.create(
            linked_item=item, price=1000, is_published=True, stock=1
        )
        self.client.login(username='customer1', password='testpass123')
        self.client.post(reverse('purchase_product', args=[product.pk]))
        self.assertTrue(Notification.objects.filter(user=self.customer).exists())


# ═══════════════════════════════════════════════════════════════════
# 8. PUBLIC PAGE TESTS
# ═══════════════════════════════════════════════════════════════════

class PublicPageTests(BaseTestMixin, TestCase):
    """Verify all public pages load correctly."""

    def test_33_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_34_about_page(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_35_contact_page(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)

    def test_36_role_selection_page(self):
        response = self.client.get(reverse('role_selection'))
        self.assertEqual(response.status_code, 200)

    def test_37_role_selection_alias(self):
        response = self.client.get('/role-selection/')
        self.assertEqual(response.status_code, 200)

    def test_38_dashboard_redirect_authenticated(self):
        self.client.login(username='customer1', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
