from app import app, db, User, Item, ItemGroup
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

# Sample data
sample_users = [
    {
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'admin123',
        'phone': '1234567890',
        'country': 'IN',
        'state': 'Delhi',
        'role': 'admin'
    },
    {
        'username': 'test_user',
        'email': 'user@example.com',
        'password': 'user123',
        'phone': '9876543210',
        'country': 'IN',
        'state': 'Maharashtra',
        'role': 'user'
    },
    {
        'username': 'john_doe',
        'email': 'john@example.com',
        'password': 'john123',
        'phone': '5551234567',
        'country': 'US',
        'state': 'California',
        'role': 'user'
    }
]

sample_items = [
    {
        'name': 'Laptop',
        'sku': 'TECH-001',
        'type': 'goods',
        'unit': 'pcs',
        'quantity_in_hand': 15,
        'reorder_point': 5,
        'cost_price': 45000,
        'selling_price': 55000,
        'tax_rate': 18,
        'returnable': True
    },
    {
        'name': 'Office Chair',
        'sku': 'FURN-001',
        'type': 'goods',
        'unit': 'pcs',
        'quantity_in_hand': 8,
        'reorder_point': 3,
        'cost_price': 3500,
        'selling_price': 4500,
        'tax_rate': 12,
        'returnable': True
    },
    {
        'name': 'Desk',
        'sku': 'FURN-002',
        'type': 'goods',
        'unit': 'pcs',
        'quantity_in_hand': 4,
        'reorder_point': 2,
        'cost_price': 6000,
        'selling_price': 8000,
        'tax_rate': 12,
        'returnable': True
    },
    {
        'name': 'Notebook',
        'sku': 'STAT-001',
        'type': 'goods',
        'unit': 'pcs',
        'quantity_in_hand': 50,
        'reorder_point': 10,
        'cost_price': 80,
        'selling_price': 120,
        'tax_rate': 5,
        'returnable': False
    },
    {
        'name': 'Printer',
        'sku': 'TECH-002',
        'type': 'goods',
        'unit': 'pcs',
        'quantity_in_hand': 3,
        'reorder_point': 2,
        'cost_price': 12000,
        'selling_price': 15000,
        'tax_rate': 18,
        'returnable': True
    },
    {
        'name': 'Web Design',
        'sku': 'SERV-001',
        'type': 'service',
        'unit': 'hrs',
        'quantity_in_hand': 0,
        'reorder_point': 0,
        'cost_price': 800,
        'selling_price': 1200,
        'tax_rate': 18,
        'returnable': False
    }
]

sample_groups = [
    {
        'name': 'Electronics',
        'type': 'goods',
        'description': 'All electronic items and accessories',
        'unit': 'pcs',
        'returnable': True,
        'manufacturer': 'Various',
        'brand': 'Mixed',
        'created_by': 'admin'
    },
    {
        'name': 'Furniture',
        'type': 'goods',
        'description': 'Office and home furniture items',
        'unit': 'pcs',
        'returnable': True,
        'manufacturer': 'Various',
        'brand': 'Mixed',
        'created_by': 'admin'
    },
    {
        'name': 'Stationery',
        'type': 'goods',
        'description': 'Office supplies and stationery items',
        'unit': 'pcs',
        'returnable': False,
        'manufacturer': 'Various',
        'brand': 'Mixed',
        'created_by': 'admin'
    },
    {
        'name': 'Services',
        'type': 'service',
        'description': 'Digital and consulting services',
        'unit': 'hrs',
        'returnable': False,
        'manufacturer': 'N/A',
        'brand': 'N/A',
        'created_by': 'admin'
    }
]

with app.app_context():
    # Clear existing data
    db.drop_all()
    db.create_all()
    
    # Add users
    for user_data in sample_users:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            password=generate_password_hash(user_data['password']),
            phone=user_data['phone'],
            country=user_data['country'],
            state=user_data['state'],
            role=user_data['role'],
            last_login=datetime.utcnow() - timedelta(days=random.randint(0, 30), 
                                                   hours=random.randint(0, 23), 
                                                   minutes=random.randint(0, 59))
        )
        db.session.add(user)
    
    # Commit users to get IDs
    db.session.commit()
    
    # Get user IDs
    admin_user = User.query.filter_by(username='admin').first()
    test_user = User.query.filter_by(username='test_user').first()
    
    # Add items
    for item_data in sample_items:
        # Assign to random user
        user_id = random.choice([admin_user.id, test_user.id])
        
        item = Item(
            name=item_data['name'],
            sku=item_data['sku'],
            type=item_data['type'],
            unit=item_data['unit'],
            quantity_in_hand=item_data['quantity_in_hand'],
            reorder_point=item_data['reorder_point'],
            cost_price=item_data['cost_price'],
            selling_price=item_data['selling_price'],
            tax_rate=item_data['tax_rate'],
            returnable=item_data['returnable'],
            user_id=user_id,
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 60)),
            updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )
        db.session.add(item)
    
    # Add groups
    for group_data in sample_groups:
        group = ItemGroup(
            name=group_data['name'],
            type=group_data['type'],
            description=group_data['description'],
            unit=group_data['unit'],
            returnable=group_data['returnable'],
            manufacturer=group_data['manufacturer'],
            brand=group_data['brand'],
            created_by=group_data['created_by'],
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 60))
        )
        db.session.add(group)
    
    # Commit all changes
    db.session.commit()
    
    print("Sample data has been created successfully!")

