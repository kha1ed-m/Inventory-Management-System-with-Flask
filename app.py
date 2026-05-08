import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change_this_in_production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    price = db.Column(db.Float, default=0.0)
    quantity = db.Column(db.Integer, default=0)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default='Pending')
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, default=0.0)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Role decorator
def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role != role:
                abort(403)
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

# Routes
@app.route('/')
def login():
    return render_template('login.html', title="Login")

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        flash("Login successful!", "success")
        return redirect(url_for('dashboard'))
    flash("Invalid credentials!", "danger")
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'Sales')
        if not username or not password:
            flash("Please provide username and password.", "danger")
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash("User registered successfully!", "success")
        return redirect(url_for('login'))
    return render_template('register.html', title="Register")

@app.route('/dashboard')
@login_required
def dashboard():
    products = Product.query.order_by(Product.id.desc()).limit(10).all()
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(5).all()
    return render_template('dashboard.html', title="Dashboard", products=products, orders=recent_orders, role=current_user.role)

# Inventory (Admin)
@app.route('/inventory')
@role_required('Admin')
def inventory():
    page = request.args.get('page', 1, type=int)
    products = Product.query.order_by(Product.id.desc()).paginate(page=page, per_page=5)
    return render_template('inventory.html', title="Inventory", products=products)

@app.route('/add_product', methods=['POST'])
@role_required('Admin')
def add_product():
    name = request.form.get('name', '').strip()
    category = request.form.get('category', '').strip()
    try:
        price = float(request.form.get('price', 0))
        quantity = int(request.form.get('quantity', 0))
    except ValueError:
        flash("Invalid price or quantity.", "danger")
        return redirect(url_for('inventory'))
    if not name:
        flash("Product name required.", "danger")
        return redirect(url_for('inventory'))
    new_product = Product(name=name, category=category, price=price, quantity=quantity)
    db.session.add(new_product)
    db.session.commit()
    flash("Product added successfully!", "success")
    return redirect(url_for('inventory'))

@app.route('/delete_product/<int:id>')
@role_required('Admin')
def delete_product(id):
    product = Product.query.get(id)
    if product:
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted!", "success")
    else:
        flash("Product not found.", "danger")
    return redirect(url_for('inventory'))

# Create Order (Sales)
@app.route('/create_order')
@role_required('Sales')
def create_order():
    products = Product.query.filter(Product.quantity > 0).all()
    return render_template('create_order.html', title="Create Order", products=products)

@app.route('/place_order', methods=['POST'])
@role_required('Sales')
def place_order():
    try:
        product_id = int(request.form.get('product_id'))
        quantity = int(request.form.get('quantity'))
    except (TypeError, ValueError):
        flash("Invalid input.", "danger")
        return redirect(url_for('create_order'))

    product = Product.query.get(product_id)
    if product and product.quantity >= quantity and quantity > 0:
        product.quantity -= quantity
        total = product.price * quantity
        new_order = Order(user_id=current_user.id, total_amount=total)
        db.session.add(new_order)
        db.session.commit()

        order_item = OrderItem(order_id=new_order.id, product_id=product.id, quantity=quantity, unit_price=product.price)
        db.session.add(order_item)
        db.session.commit()

        flash(f"Order #{new_order.id} placed successfully!", "success")
        return redirect(url_for('view_orders'))
    else:
        flash("Not enough stock or invalid quantity.", "danger")
        return redirect(url_for('create_order'))

# View Orders (Sales)
@app.route('/orders')
@role_required('Sales')
def view_orders():
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).paginate(page=page, per_page=5)
    return render_template('orders.html', title="My Orders", orders=orders)

@app.route('/order/<int:id>')
@role_required('Sales')
def order_details(id):
    order = Order.query.get(id)
    if not order or order.user_id != current_user.id:
        abort(403)
    items = OrderItem.query.filter_by(order_id=id).all()
    detailed_items = []
    for it in items:
        prod = Product.query.get(it.product_id)
        detailed_items.append({'product_name': prod.name if prod else 'Deleted', 'quantity': it.quantity, 'unit_price': it.unit_price})
    return render_template('order_details.html', title="Order Details", order=order, items=detailed_items)

# Reports (Admin)
@app.route('/reports')
@role_required('Admin')
def reports():
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_sales = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    low_stock = Product.query.filter(Product.quantity < 5).all()
    return render_template('reports.html', title="Reports",
                           total_products=total_products,
                           total_orders=total_orders,
                           total_sales=total_sales,
                           low_stock=low_stock)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for('login'))

# Ensure DB exists (if user didn't run int_db.py)
if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        with app.app_context():
            db.create_all()
            print("database.db created (from app). For controlled schema use int_db.py with schema.sql.")
    app.run(debug=True)
