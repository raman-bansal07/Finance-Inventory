from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import random
from decimal import Decimal
import json
from functools import wraps
# from chatbot import chatbot_bp
import os
from flask import Flask, render_template
from chatbot import chatbot_bp# Import the chatbot Blueprint

app = Flask(__name__)
# Register the chatbot Blueprint
app.register_blueprint(chatbot_bp)

# New route for chatbot UI
@app.route('/chatbot-ui')
def chatbot_ui():
    return render_template("chatbot_ui.html")  # Updated file name

# os.environ['CHATBOT_API_KEY'] = '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'  # Replace with your actual API key
# os.environ['CHATBOT_API_URL'] = 'https://openrouter.ai/api/v1'  # Replace with your actual API URL
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
# app.register_blueprint(chatbot_bp)

db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = 'users'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    country = db.Column(db.String(50))
    state = db.Column(db.String(50))
    role = db.Column(db.String(20), default='user')  # 'admin' or 'user'
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('Item', backref='owner', lazy=True)

class Item(db.Model):
    __tablename__ = 'items'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True)
    type = db.Column(db.String(50))  # goods or service
    unit = db.Column(db.String(20))
    quantity_in_hand = db.Column(db.Integer, default=0)
    reorder_point = db.Column(db.Integer, default=5)
    cost_price = db.Column(db.Float)
    selling_price = db.Column(db.Float, nullable=False)
    tax_rate = db.Column(db.Float)
    returnable = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ItemGroup(db.Model):
    __tablename__ = 'item_groups'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))  # goods or service
    description = db.Column(db.Text)
    unit = db.Column(db.String(20))
    returnable = db.Column(db.Boolean, default=True)
    manufacturer = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Decorators for route protection
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'danger')
            return redirect(url_for('loginFunction'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'danger')
            return redirect(url_for('loginFunction'))
        
        user = User.query.get(session['user_id'])
        if user.role != 'admin':
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('home'))
        
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def home():
    is_authenticated = 'user_id' in session
    user = None
    if is_authenticated:
        user = User.query.get(session['user_id'])
    return render_template('index.html', is_authenticated=is_authenticated, user=user)

@app.route('/login', methods=['GET', 'POST'])
def loginFunction():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session.permanent = True
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def registerFunction():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        country = request.form['country']
        state = request.form['state']
        
        # Check if user already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists!', 'danger')
            return redirect(url_for('registerFunction'))
        
        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            phone=phone,
            country=country,
            state=state,
            role='user'  # Default role
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('loginFunction'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        user = User.query.get(session['user_id'])
        
        if not check_password_hash(user.password, current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('change_password'))
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('change_password'))
        
        user.password = generate_password_hash(new_password)
        db.session.commit()
        
        flash('Password updated successfully', 'success')
        return redirect(url_for('profile'))
        
    return render_template('change_password.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    
    # Get some dashboard stats
    total_items = Item.query.filter_by(user_id=user.id).count()
    items = Item.query.filter_by(user_id=user.id).all()
    
    total_inventory_value = sum(item.cost_price * item.quantity_in_hand for item in items if item.cost_price) or 0
    avg_item_value = total_inventory_value / total_items if total_items > 0 else 0
    
    low_stock_items = sum(1 for item in items if item.quantity_in_hand <= item.reorder_point and item.quantity_in_hand > 0)
    out_of_stock_items = sum(1 for item in items if item.quantity_in_hand == 0)
    
    high_value_items = sum(1 for item in items if item.cost_price and item.cost_price > 1000)  # Arbitrary threshold
    
    # Get top items by value
    top_value_items = sorted(items, key=lambda x: (x.cost_price or 0) * x.quantity_in_hand, reverse=True)[:5]
    
    # Get tax distribution
    tax_rates = {}
    for item in items:
        rate = item.tax_rate
        tax_rates[rate] = tax_rates.get(rate, 0) + 1
    
    tax_distribution = sorted(tax_rates.items(), key=lambda x: x[0] or 0)
    
    # Get top margin items
    top_margin_items = []
    for item in items:
        if item.cost_price and item.selling_price:
            margin = ((item.selling_price - item.cost_price) / item.cost_price) * 100
            top_margin_items.append((item, margin))
    
    top_margin_items = sorted(top_margin_items, key=lambda x: x[1], reverse=True)[:5]
    
    # Item group stats
    groups = ItemGroup.query.all()
    total_groups = len(groups)
    goods_groups = sum(1 for group in groups if group.type == 'goods')
    service_groups = sum(1 for group in groups if group.type == 'service')
    returnable_groups = sum(1 for group in groups if group.returnable)
    
    # Recent groups
    recent_groups = sorted(groups, key=lambda x: x.created_at, reverse=True)[:5]
    
    # Unit distribution
    unit_counts = {}
    for group in groups:
        unit = group.unit
        unit_counts[unit] = unit_counts.get(unit, 0) + 1
    
    unit_distribution = sorted(unit_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Groups with attributes (placeholder)
    groups_with_attributes = [(group, random.randint(1, 5)) for group in recent_groups]
    
    items_to_receive = random.randint(0, 10)  # Placeholder
    returnable_items = sum(1 for item in items if item.returnable)
    
    return render_template(
        'dashboard.html',
        total_items=total_items,
        total_inventory_value=total_inventory_value,
        avg_item_value=avg_item_value,
        low_stock_items=low_stock_items,
        out_of_stock_items=out_of_stock_items,
        high_value_items=high_value_items,
        top_value_items=top_value_items,
        tax_distribution=tax_distribution,
        top_margin_items=top_margin_items,
        total_groups=total_groups,
        goods_groups=goods_groups,
        service_groups=service_groups,
        returnable_groups=returnable_groups,
        recent_groups=recent_groups,
        unit_distribution=unit_distribution,
        groups_with_attributes=groups_with_attributes,
        items_to_receive=items_to_receive,
        returnable_items=returnable_items
    )

@app.route('/inventory')
@login_required
def inventory():
    return render_template('inventory.html')

@app.route('/item_form', methods=['GET', 'POST'])
@login_required
def item_form():
    if request.method == 'POST':
        name = request.form.get('item-name')
        item_type = request.form.get('type', 'goods')
        sku = request.form.get('item-sku')
        unit = request.form.get('item-unit')
        selling_price = request.form.get('selling-price')
        cost_price = request.form.get('cost-price')
        tax_rate = request.form.get('tax-rate')
        returnable = request.form.get('returnable') == '1'
        
        # Validation
        if not name or not unit or not selling_price:
            flash('Name, unit, and selling price are required', 'danger')
            return redirect(url_for('item_form'))
        
        # Create new item
        new_item = Item(
            name=name,
            type=item_type,
            sku=sku,
            unit=unit,
            selling_price=float(selling_price),
            cost_price=float(cost_price) if cost_price else None,
            tax_rate=float(tax_rate) if tax_rate else None,
            returnable=returnable,
            user_id=session['user_id'],
            quantity_in_hand=0,
            reorder_point=5
        )
        
        db.session.add(new_item)
        db.session.commit()
        
        flash('Item added successfully', 'success')
        return redirect(url_for('item_list'))
    
    return render_template('item_form.html')

@app.route('/items')
@login_required
def item_list():
    user = User.query.get(session['user_id'])
    items = Item.query.filter_by(user_id=user.id).all()
    
    # Calculate total value
    total_value = sum(item.cost_price * item.quantity_in_hand for item in items if item.cost_price) or 0
    
    # Get item types
    item_types = {}
    for item in items:
        item_type = item.type or 'Other'
        item_types[item_type] = item_types.get(item_type, 0) + 1
    
    return render_template(
        'item_list.html', 
        items=items,
        total_items=len(items),
        total_value=total_value,
        item_types=item_types
    )

@app.route('/items/update/<int:id>', methods=['POST'])
@login_required
def update_item(id):
    item = Item.query.get_or_404(id)
    
    # Check if the item belongs to the logged-in user
    if item.user_id != session['user_id']:
        flash('You do not have permission to edit this item', 'danger')
        return redirect(url_for('item_list'))
    
    item.name = request.form['name']
    item.sku = request.form['sku']
    item.unit = request.form['unit']
    item.quantity_in_hand = int(request.form['quantity_in_hand'])
    item.reorder_point = int(request.form['reorder_point'])
    item.selling_price = float(request.form['selling_price'])
    
    if request.form['cost_price']:
        item.cost_price = float(request.form['cost_price'])
    
    if request.form['tax_rate']:
        item.tax_rate = float(request.form['tax_rate'])
    
    item.returnable = 'returnable' in request.form
    item.updated_at = datetime.utcnow()
    
    db.session.commit()
    flash('Item updated successfully', 'success')
    return redirect(url_for('item_list'))

@app.route('/items/delete/<int:id>', methods=['POST'])
@login_required
def delete_item(id):
    item = Item.query.get_or_404(id)
    
    # Check if the item belongs to the logged-in user
    if item.user_id != session['user_id']:
        flash('You do not have permission to delete this item', 'danger')
        return redirect(url_for('item_list'))
    
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully', 'success')
    return redirect(url_for('item_list'))

@app.route('/groups', methods=['GET', 'POST'])
@login_required
def groups():
    if request.method == 'POST':
        name = request.form.get('itemGroupName')
        item_type = request.form.get('type', 'goods')
        description = request.form.get('description')
        unit = request.form.get('unit')
        manufacturer = request.form.get('manufacturer')
        brand = request.form.get('brand')
        returnable = 'returnable' in request.form
        
        # Create new item group
        user = User.query.get(session['user_id'])
        new_group = ItemGroup(
            name=name,
            type=item_type,
            description=description,
            unit=unit,
            manufacturer=manufacturer,
            brand=brand,
            returnable=returnable,
            created_by=user.username
        )
        
        db.session.add(new_group)
        db.session.commit()
        
        flash('Item group created successfully', 'success')
        return redirect(url_for('inventory'))
    
    return render_template('group_form.html')

@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    # Get all users
    users = User.query.all()
    total_users = len(users)
    admin_users = sum(1 for user in users if user.role == 'admin')
    regular_users = total_users - admin_users
    
    # Get inventory data
    items = Item.query.all()
    total_inventory_value = sum(item.cost_price * item.quantity_in_hand for item in items if item.cost_price) or 0
    
    # Stock alerts
    low_stock_items = sum(1 for item in items if item.quantity_in_hand <= item.reorder_point and item.quantity_in_hand > 0)
    out_of_stock_items = sum(1 for item in items if item.quantity_in_hand == 0)
    
    # Recent user activity
    recent_users = sorted(users, key=lambda x: x.last_login if x.last_login else datetime.min, reverse=True)[:10]
    
    # High value items
    high_value_items = sorted(items, key=lambda x: (x.cost_price or 0), reverse=True)[:10]
    
    # Price distribution for chart (placeholder)
    price_distribution = [
        {"range": "₹0-500", "count": random.randint(10, 50)},
        {"range": "₹501-1000", "count": random.randint(5, 30)},
        {"range": "₹1001-5000", "count": random.randint(3, 20)},
        {"range": "₹5001+", "count": random.randint(1, 10)}
    ]
    
    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        admin_users=admin_users,
        regular_users=regular_users,
        total_inventory_value=total_inventory_value,
        low_stock_items=low_stock_items,
        out_of_stock_items=out_of_stock_items,
        recent_users=recent_users,
        high_value_items=high_value_items,
        price_distribution=price_distribution
    )

@app.route('/admin/users/manage', methods=['GET', 'POST'])
@admin_required
def manage_users():
    if request.method == 'POST':
        if 'action' in request.form and request.form['action'] == 'toggle_status':
            user_id = int(request.form['user_id'])
            user = User.query.get(user_id)
            
            # Simple toggle between active and disabled (you can expand this)
            if user.role == 'admin':
                user.role = 'user'
            else:
                user.role = 'admin'
                
            db.session.commit()
            return jsonify({"success": True})
        else:
            # Add new user
            username = request.form['username']
            email = request.form['email']
            role = request.form['role']
            
            # Generate a random password
            temp_password = ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(12))
            hashed_password = generate_password_hash(temp_password)
            
            new_user = User(
                username=username,
                email=email,
                password=hashed_password,
                role=role
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            # In a real app, you would send this password to the user via email
            return jsonify({"success": True, "message": f"User created with temporary password: {temp_password}"})
    
    # GET request - return list of users
    users_data = []
    for user in User.query.all():
        users_data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "status": "Active",  # You can add a status field to your model if needed
            "last_login": user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None
        })
    
    return jsonify(users_data)

@app.route('/about')
def about_us():
    return render_template('about_us.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# Route to reset the database
@app.route('/reset_db', methods=['GET'])
def reset_db():
    # Only allow this in development
    if app.debug:
        db.drop_all()
        db.create_all()
        
        # Create admin user
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('admin123'),
            phone='1234567890',
            country='IN',
            state='Delhi',
            role='admin'
        )
        db.session.add(admin_user)

        admin_user = User(
            username='raman07',
            email='raman07@example.com',
            password=generate_password_hash('admin07'),
            phone='1234567890',
            country='IN',
            state='Delhi',
            role='admin'
        )
        db.session.add(admin_user)
        
        # Create test user
        test_user = User(
            username='test_user',
            email='user@example.com',
            password=generate_password_hash('user123'),
            phone='9876543210',
            country='IN',
            state='Maharashtra',
            role='user'
        )
        db.session.add(test_user)
        
        db.session.commit()
        
        flash('Database has been reset successfully!', 'success')
        return redirect(url_for('home'))
    else:
        return "This route is only available in development mode", 403

if __name__ == '__main__':
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Check if admin user exists, if not create one
        admin_exists = User.query.filter_by(role='admin').first()
        if not admin_exists:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                phone='1234567890',
                country='IN',
                state='Delhi',
                role='admin'
            )
            db.session.add(admin_user)
            
            # Also create a test user
            test_user = User(
                username='test_user',
                email='user@example.com',
                password=generate_password_hash('user123'),
                phone='9876543210',
                country='IN',
                state='Maharashtra',
                role='user'
            )
            db.session.add(test_user)
            
            db.session.commit()
            
    app.run(debug=True)

