from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from models import User, Product, Cart, Notification
from forms import LoginForm, RegistrationForm, ProductForm

@app.route('/')
def home():
    products = Product.query.all()
    return render_template('home.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user.role == 'salesperson':
            return redirect(url_for('salesperson_dashboard'))
        return redirect(url_for('home'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role='user')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    return render_template('admin_dashboard.html')

@app.route('/salesperson_dashboard', methods=['GET', 'POST'])
@login_required
def salesperson_dashboard():
    if current_user.role != 'salesperson':
        return redirect(url_for('home'))
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data, price=form.price.data, description=form.description.data)
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!')
        return redirect(url_for('salesperson_dashboard'))
    products = Product.query.all()
    return render_template('salesperson_dashboard.html', form=form, products=products)

@app.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@app.route('/cart')
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    return render_template('cart.html', cart_items=cart_items)

@app.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart_item = Cart(user_id=current_user.id, product_id=product.id, quantity=1)
    db.session.add(cart_item)
    db.session.commit()
    flash('Product added to cart')
    return redirect(url_for('cart'))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    products = Product.query.filter(Product.name.contains(query)).all()
    return render_template('search_results.html', products=products)

@app.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).all()
    return render_template('notifications.html', notifications=notifications)