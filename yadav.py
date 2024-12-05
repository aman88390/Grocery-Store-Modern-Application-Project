import os
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import func
import matplotlib.pyplot as plt
import io
import base64
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt



app = Flask(__name__)
app.secret_key= secrets.token_hex(16)

base_dir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'Userdatabase.db')
db = SQLAlchemy(app)
#models
class User(db.Model):
    First_name=db.Column(db.String, nullable=False)
    Last_name=db.Column(db.String, nullable=True)
    email=db.Column(db.String,nullable=False, unique=True, primary_key=True)
    mobile_number=db.Column(db.String(10),nullable=False)
    username=db.Column(db.String(17),unique=True, nullable=False)
    Password=db.Column(db.String(17),nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    unit=db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    exp=db.Column(db.String, nullable=False)
    stock = db.Column(db.Float,nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id',ondelete='CASCADE'), nullable=False)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.email'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref='cart_items')
    product = db.relationship('Product', backref='cart_items')

class PurchaseHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  
    product_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=False) 



@app.route('/')
def front_page():
    return render_template('front_page.html')


@app.route('/search_page', methods=['GET'])
def search_page():
    query = request.args.get('query', '').strip()

    categories = Category.query.filter(Category.name.ilike(f'%{query}%')).all()
    products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    product_price=Product.query.filter(Product.price.ilike(f'%{query}%')).all()

    return render_template('search_page.html', query=query,product_price=product_price, categories=categories, products=products)




@app.route('/Manager_login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['managername']
        password = request.form['Psrd']
        if username == 'aman' and password == '1234':
            return redirect('manager_dashboard')
        else:
            message = 'Invalid username or password.'
            return render_template('Manager_login.html', message=message)
    else:
        return render_template('Manager_login.html')

@app.route('/search_admin')
def search_admin():
    query = request.args.get('query', '').strip()
    categories = Category.query.filter(Category.name.ilike(f'%{query}%')).all()
    product = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    product_price= Product.query.filter(Product.price.ilike(f'%{query}%')).all()
    avl=Product.query.filter(Product.stock.ilike(f'%{query}%')).all()
    return render_template("search_admin.html",query=query, categories=categories, avl=avl,product=product, product_price=product_price)
    

@app.route('/manager_logout')
def man_log():
    return render_template('front_page.html')

@app.route("/user_login")
def usr_login():
    return render_template('user_login.html')


@app.route('/user_login', methods=['POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['Password']

        user = User.query.filter_by(username=username,Password=password).first()
        
        if user :
            session['user_id'] = user.email
            return redirect(url_for('user_dashboard'))
        else:
            message="Invalid password or username"
            return render_template("user_login.html", message=message)

    return render_template('user_login.html')
@app.route('/user_logout')
def logout():
    session.pop('user_id', None)

    return render_template('front_page.html')
       

@app.route("/New User")
def new_use():
    return render_template("New_reg.html")

@app.route("/New User", methods=["POST"])
def new_user():
    if request.method=="POST":
        first_name=request.form["First_name"]
        last_name=request.form['Last_name']
        email = request.form['Email']
        mobile_number = request.form['Mobile_number']
        username = request.form.get('User_name')
        password = request.form.get('Password')
        confirm_password = request.form.get('Confirm_password')

        exist_user = User.query.filter_by(email=email).first()

        if exist_user:
            message="User already exist,try with different email or username"
            return render_template('New_reg.html', message=message) 
        elif password == confirm_password:

            new_user = User(
                First_name=first_name,
                Last_name=last_name,
                email=email,
                mobile_number=mobile_number,
                username=username,
                Password=password
            )

            db.session.add(new_user)
            db.session.commit()
            return render_template('wel_msg.html',name=first_name,lname=last_name)
        else:
            last="Password do not match"
            return render_template("New_reg.html",message=last)

    return render_template('New_reg.html')


@app.route('/manager_dashboard')
def manager_dashboard():
    categories = Category.query.all()
    return render_template('manager_dashboard.html', categories=categories)



@app.route('/add_category')
def add_category_page():
    return render_template('Add_category.html')

@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form['name']
    id = request.form['id']
    exist_category=Category.query.filter_by(id=id).first()
    if exist_category:
        message="Category ID Already Exited.Please Try with new category ID"
        return render_template('Add_category.html',message=message)
    
    category = Category(name=name,id=id)

    db.session.add(category)
    db.session.commit()
    
    return render_template('invalid.html')
  
    
@app.route('/edit_category')
def edit_category_page():
    return render_template('edit_category.html')

@app.route('/edit_category/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get(id)
    if request.method == 'POST':
        category.name = request.form['name']
        category.id=request.form['id']
        db.session.commit()
        return redirect(url_for('manager_dashboard'))
    else:
        
        return render_template('edit_category.html', category=category) 


@app.route("/delete_category")
def delete_category_page():
    return render_template("delete_category.html")


@app.route('/delete_category/<int:id>', methods=["GET","POST"])
def delete_category(id):
    category=Category.query.get(id)
    if request.method=='POST':
        products=category.products
        for product in products:
            cart_item=CartItem.query.filter_by(product_id=product.product_id).all()
            for cart_item in cart_item:
                db.session.delete(cart_item)
            db.session.delete(product)
       
        db.session.delete(category)
        db.session.commit()
        return redirect(url_for('manager_dashboard'))
    return render_template("delete_category.html", category=category)
    

@app.route('/add_product', methods=['POST','GET'])
def add_product():
    categories = Category.query.all()
    if request.method=="POST":
      product_id=request.form['product_id']
      name = request.form['name']
      unit=request.form['unit']
      price = float(request.form['price'])
      exp=request.form['exp']
      category_id = request.form['category_id']
      stock=float(request.form['stock'])
      exist_prod=Product.query.filter_by(product_id=product_id).first()
      if exist_prod:
        message="Product ID already exist. Please try with new ID"
        return render_template('Add_product.html',categories=categories, message=message)
      product = Product(product_id=product_id,name=name, price=price, category_id=category_id,stock=stock,unit=unit,exp=exp)
      db.session.add(product)
      db.session.commit()
      return redirect(url_for('manager_dashboard'))
    
    return render_template('Add_product.html',categories=categories )



@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get(product_id)
    categories = Category.query.all()
    if request.method == 'POST':
        product.name = request.form['name']
        product.unit = request.form['unit']
        product.price = float(request.form['price'])
        product.expiry_date = request.form['exp']
        product.category_id = int(request.form['category_id'])
        product.stock = float(request.form['stock'])
        db.session.commit()
        return redirect(url_for('manager_dashboard'))
    else:
        categories = Category.query.all()
        return render_template('edit_product.html', product=product, categories=categories)


@app.route('/delete_product/<int:product_id>', methods=["GET",'POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method=="POST":
      cart_items = CartItem.query.filter_by(product_id=product_id).all()
      for cart_item in cart_items:
            db.session.delete(cart_item)

      db.session.delete(product)
      db.session.commit()
      return redirect(url_for('manager_dashboard'))
    else:
      return render_template("delete_product.html",product=product)


@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_login'))
    
    user = User.query.get(user_id)
    if not user:
        return "User not found"
    
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        return redirect(url_for('search_reults', query=query))
    categories = Category.query.all()
    products = Product.query.all()

    return render_template('user_dashboard.html', user=user, categories=categories, products=products)

@app.route('/search_results', methods=['GET'])
def search_results():
    query = request.args.get('query', '').strip()

    categories = Category.query.filter(Category.name.ilike(f'%{query}%')).all()
    products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    product_price=Product.query.filter(Product.price.ilike(f'%{query}%')).all()

    return render_template('search_results.html', query=query,product_price=product_price, categories=categories, products=products)



@app.route('/add_cart/<int:product_id>', methods=['GET','POST'])
def add_cart(product_id):
    user_id = session.get('user_id')
    if user_id:
        product = Product.query.get(product_id)
        return render_template('select.html',product=product)
    else:
        return redirect(url_for('user_login'))


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    user_id = session.get('user_id')
    if user_id:
        quantity = float(request.form['quantity'])
        product = Product.query.get(product_id)

        if quantity <= 0 or quantity > product.stock:
            message="OUT OF STOCK"
            return render_template('select.html', message=message, product=product)
        else:    
           cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
        if cart_item:
            cart_item.quantity = cart_item.quantity + quantity
        else:
            cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)

        product.stock =product.stock- quantity
        db.session.add(cart_item)
        db.session.commit()

        return redirect(url_for('my_cart'))
    else:
        return redirect(url_for('user_login'))

@app.route('/my_cart')
def my_cart():
    user_id = session.get('user_id')
    if user_id:
        product=Product.query.all()
        user = User.query.get(user_id)
        cart_items = user.cart_items
        total_price = 0

        for cart_item in cart_items:
            total_price = total_price+( cart_item.product.price * cart_item.quantity)

        grand_total = total_price  

        return render_template('my_cart.html', cart_items=cart_items, total_price=total_price, grand_total=grand_total,product=product)
    else:
        return redirect(url_for('user_login'))
@app.route('/buy')
def guy():
    return render_template('purchase.html')
@app.route('/buy', methods=["GET","POST"])
def buy():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_login'))
    if user_id:
        cart_items = CartItem.query.filter_by(user_id=user_id).all()

        for cart_item in cart_items:
            purchase = PurchaseHistory(
               user_id=user_id,
               product_name=cart_item.product.name,
               price=cart_item.product.price,
               quantity=cart_item.quantity,
               purchase_date=datetime.now())
            db.session.add(purchase)
            db.session.delete(cart_item)

            db.session.commit()

        return redirect(url_for('purchase'))
    return redirect(url_for('my_cart'))


@app.route('/purchasehistory')
def purchasehistory():
    user_id = session.get('user_id')
    if not user_id:
        return render_template('user_login.html')
    
    purchase_history = PurchaseHistory.query.filter_by(user_id=user_id).all()

    return render_template('purchasehistory.html', purchase_history=purchase_history)

@app.route('/purchase')
def purchase():
    return render_template('purchase.html')




@app.route('/product_summary')
def sales_summary():
    product_summary = sales_summary()
    img_data = sales_graph(product_summary)
    stock_data = stock() 
    return render_template('summary.html', img_data=img_data, plot_url=stock_data)

def sales_graph(product_summary):
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt

    product_names = [product[0] for product in product_summary]
    total_quantities = [product[1] for product in product_summary]

    plt.bar(product_names, total_quantities, color='blue', edgecolor="black")
    plt.xlabel('Product')
    plt.ylabel('Total Quantity Sold')
    plt.title('Product Sales Summary - This Week')
    plt.xticks(rotation=45) 
    plt.tight_layout() 

    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png')
    img_stream.seek(0)
    
    plt.close()
    img_data = base64.b64encode(img_stream.read()).decode()

    return img_data

def stock():
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt

    products = Product.query.all()

    product_names = [product.name for product in products]
    stock_values = [product.stock for product in products]

    plt.bar(product_names, stock_values, color="green")
    plt.xlabel('Product')
    plt.ylabel('Available Stock')
    plt.title('Available Stock for Products')
    plt.xticks(rotation=45)
    plt.tight_layout()

    image = io.BytesIO()
    plt.savefig(image, format='png')
    plt.close()
    image.seek(0)
    plot_url = base64.b64encode(image.read()).decode()

    return plot_url

def sales_summary():
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    product_summary = db.session.query(
        PurchaseHistory.product_name,
        db.func.sum(PurchaseHistory.quantity).label('total_quantity')
    ).filter(
        PurchaseHistory.purchase_date >= start_of_week,
        PurchaseHistory.purchase_date <= end_of_week
    ).group_by(PurchaseHistory.product_name).all()
    
    return product_summary






if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)