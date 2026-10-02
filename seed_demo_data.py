import os
import django
import random
from datetime import timedelta
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efixhub.settings')
django.setup()

from core.models import (
    CustomUser, CustomerProfile, AgentProfile, MechanicProfile,
    EWasteItem, RepairLog, Product, Order, Notification, ActivityLog, Gallery
)
from django.db import transaction

def clear_data():
    print("🧹 Cleaning existing data...")
    ActivityLog.objects.all().delete()
    Notification.objects.all().delete()
    Order.objects.all().delete()
    Product.objects.all().delete()
    RepairLog.objects.all().delete()
    EWasteItem.objects.all().delete()
    # Keep the superuser 'admin' if it exists, otherwise it will be created
    CustomUser.objects.exclude(username='admin').delete()
    Gallery.objects.all().delete()

def create_demo_data():
    print("🚀 Generating demo data...")

    # 1. Create Admins
    if not CustomUser.objects.filter(username='admin').exists():
        admin = CustomUser.objects.create_superuser(
            username='admin', email='admin@efixhub.local', password='admin123',
            role='ADMIN', phone='1000000000', state='Kerala', district='Kochi', address='Main Office'
        )
        print("✅ Created Admin: admin/admin123")
    else:
        admin = CustomUser.objects.get(username='admin')

    # 2. Create Customers
    customers = []
    for i in range(1, 4):
        username = f'customer{i}'
        email = f'cust{i}@test.com'
        user = CustomUser.objects.create_user(
            username=username, email=email, password='password123',
            role='CUSTOMER', phone=f'900000000{i}', state='Kerala', district='Kochi'
        )
        CustomerProfile.objects.create(user=user, phone=user.phone, address=f'Customer Address {i}')
        customers.append(user)
    print(f"✅ Created {len(customers)} Customers")

    # 3. Create Agents
    agents = []
    for i in range(1, 3):
        username = f'agent{i}'
        user = CustomUser.objects.create_user(
            username=username, email=f'agent{i}@test.com', password='password123',
            role='AGENT', phone=f'800000000{i}', state='Kerala', district='Kochi'
        )
        AgentProfile.objects.create(
            user=user, qualification='Degree', experience=i+1,
            verification_status='Approved', is_available=True
        )
        agents.append(user)
    print(f"✅ Created {len(agents)} Agents")

    # 4. Create Mechanics
    mechanics = []
    specializations = ['Mobile Phones', 'Laptops', 'Televisions']
    for i in range(1, 4):
        username = f'mechanic{i}'
        user = CustomUser.objects.create_user(
            username=username, email=f'mechanic{i}@test.com', password='password123',
            role='MECHANIC', phone=f'700000000{i}', state='Kerala', district='Kochi'
        )
        MechanicProfile.objects.create(
            user=user, specialization=specializations[i-1], qualification='ITI/Diploma',
            workshop_address=f'Workshop Street {i}', verification_status='Approved'
        )
        mechanics.append(user)
    print(f"✅ Created {len(mechanics)} Mechanics")

    # 5. Create E-waste Items (in various stages)
    categories = ['Mobile', 'Laptop', 'TV', 'Appliance']
    
    # Test Image
    dummy_img = SimpleUploadedFile(
        name='demo.jpg', 
        content=b'\x47\x49\x46\x38\x89\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\xff\xff\xff\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b', 
        content_type='image/gif'
    )

    items = []
    statuses = [
        'Pending', 'Approved', 'Assigned to Agent', 'Collected', 
        'Assigned to Mechanic', 'Restoration in Progress', 'Restoration Complete',
        'Repaired', 'Converted to Product', 'Sold Out'
    ]

    for i in range(10):
        cust = random.choice(customers)
        status = statuses[i % len(statuses)]
        item = EWasteItem.objects.create(
            uploaded_by=cust,
            title=f'Device {i+1} ({categories[i%4]})',
            category=categories[i%4],
            description=f'Description for device {i+1}',
            condition='Broken/Used',
            status=status,
            repair_progress=100 if status in ['Restoration Complete', 'Repaired', 'Converted to Product', 'Sold Out'] else (50 if status == 'Restoration in Progress' else 0),
            collection_district='Kochi',
            collection_address='Pickup location text',
            image=dummy_img
        )
        
        # Link assignments based on status
        if status in ['Assigned to Agent', 'Collected']:
            item.assigned_agent = random.choice(agents)
        if status in ['Assigned to Mechanic', 'Restoration in Progress', 'Restoration Complete', 'Repaired', 'Converted to Product', 'Sold Out']:
            item.assigned_mechanic = random.choice(mechanics)
        
        item.save()
        items.append(item)

        # Create RepairLog for completed repairs
        if status in ['Restoration Complete', 'Repaired', 'Converted to Product', 'Sold Out']:
            RepairLog.objects.create(
                item=item,
                mechanic=item.assigned_mechanic or random.choice(mechanics),
                repair_notes='Full restoration complete. Replaced internal components.',
                cost=random.randint(500, 5000),
                is_paid=random.choice([True, False])
            )

        # Create Product for 'Converted to Product' and 'Sold Out'
        if status in ['Converted to Product', 'Sold Out']:
            prod = Product.objects.create(
                linked_item=item,
                price=random.randint(5000, 25000),
                is_published=True,
                is_sold=(status == 'Sold Out'),
                stock=0 if status == 'Sold Out' else 1
            )
            
            # Create Order for 'Sold Out'
            if status == 'Sold Out':
                Order.objects.create(
                    product=prod,
                    buyer=random.choice(customers),
                    total_price=prod.price,
                    status='Delivered',
                    payment_method='COD',
                    shipping_name='Test Buyer',
                    shipping_address='Delivery Address'
                )

    print(f"✅ Created {len(items)} E-waste items with various statuses")

    print("\n✨ SEEDING COMPLETE! ✨")
    print("You can now login as:")
    print("- Admin: admin / admin123")
    print("- Customer: customer1 / password123")
    print("- Agent: agent1 / password123")
    print("- Mechanic: mechanic1 / password123")

if __name__ == "__main__":
    with transaction.atomic():
        clear_data()
        create_demo_data()
