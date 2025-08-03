from flask import render_template
from flask_mailman import EmailMessage
import base64
import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Message, Mail
from flask_mailman import Mail, EmailMessage

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/revivo_db'
app.config['SECRET_KEY'] = 'Fiza_Ashfaq_09'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'jco2024ppsc4@gmail.com'
app.config['MAIL_PASSWORD'] = 'gkph viyh vcqs lube'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)
# gkph viyh vcqs lube


def send_order_confirmation_email(user_email, order_details):
    msg = EmailMessage(
        subject='Order Confirmation',
        body=render_template('order_confirmation_email.txt',
                             order_details=order_details),
        from_email='jco2024ppsc4@gmail.com',
        to=[user_email]
    )

    with app.app_context():
        try:
            msg.send()
            print(f"Email sent to {user_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")


db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)


class LenderForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    lender_city = db.Column(db.String(100), nullable=False)
    Dres_type = db.Column(db.String(100), nullable=False)
    other_lender_city = db.Column(db.String(100), nullable=True)
    price_of_a_dress = db.Column(db.Integer, nullable=True)
    Brand = db.Column(db.String(100), nullable=True)
    Size = db.Column(db.String(100), nullable=True)
    date_of_purchase = db.Column(db.Date, nullable=True)
    dress_info = db.Column(db.Text, nullable=True)
    image = db.Column(db.LargeBinary, nullable=True)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address_line_1 = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postalcode = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    card_number = db.Column(db.String(20))
    card_type = db.Column(db.String(20))
    expiry_month = db.Column(db.String(2))
    expiry_year = db.Column(db.String(4))
    cvv = db.Column(db.String(4))
    jazzcash_number = db.Column(db.String(20))
    easypaisa_number = db.Column(db.String(20))
    total_price = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    order_items = db.relationship('OrderItem', backref='order', lazy=True)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)


# Custom AdminIndexView to add authentication


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not session.get('admin'):
            return redirect(url_for('login'))
        return super(MyAdminIndexView, self).index()

# Secured ModelView


class SecuredModelView(ModelView):
    def is_accessible(self):
        return session.get('admin')


admin = Admin(app, name='Admin Panel', template_mode='bootstrap4',
              index_view=MyAdminIndexView())
admin.add_view(SecuredModelView(User, db.session))
admin.add_view(SecuredModelView(LenderForm, db.session))
admin.add_view(SecuredModelView(Order, db.session))
admin.add_view(SecuredModelView(OrderItem, db.session))
admin.add_view(SecuredModelView(Feedback, db.session))


def get_dress_by_id(dress_id):
    dress = LenderForm.query.get(dress_id)
    if not dress:
        abort(404)
    image_base64 = base64.b64encode(dress.image).decode(
        'utf-8') if dress.image else None
    return dress


@app.route("/")
def index():
    return render_template('home.html')


@app.route("/details")
def details():
    return render_template('details.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            if user.username == 'admin':  # or use a proper admin check
                session['admin'] = True
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('/auth/Login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('admin', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists', 'danger')
            return redirect(url_for('signup'))

        new_user = User(username=username, email=email, password=generate_password_hash(
            password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('/auth/SignUp.html')


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Fetch form data
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address_line_1 = request.form['address_line_1']
        city = request.form['city']
        state = request.form['state']
        postalcode = request.form['postalcode']
        phone = request.form['phone']
        payment_method = request.form['payment_method']

        # Initialize payment fields
        card_number = None
        card_type = None
        expiry_month = None
        expiry_year = None
        cvv = None
        jazzcash_number = None
        easypaisa_number = None

        # Prepare payment details based on payment method
        if payment_method == 'card':
            card_number = request.form['card_number']
            card_type = request.form['card_type']
            expiry_month = request.form['expiry_month']
            expiry_year = request.form['expiry_year']
            cvv = request.form['cvv']
        elif payment_method == 'jazzcash':
            jazzcash_number = request.form['jazzcash_number']
        elif payment_method == 'easypaisa':
            easypaisa_number = request.form['easypaisa_number']

        # Calculate total price
        cart_items = session.get('cart', [])
        total_price = sum(item['price_of_a_dress'] * item['quantity']
                          for item in cart_items) + 20

        # Create new order object
        new_order = Order(
            email=email, first_name=first_name, last_name=last_name,
            address_line_1=address_line_1, city=city, state=state,
            postalcode=postalcode, phone=phone, card_number=card_number,
            card_type=card_type, expiry_month=expiry_month,
            expiry_year=expiry_year, cvv=cvv, jazzcash_number=jazzcash_number,
            easypaisa_number=easypaisa_number, total_price=total_price,
            payment_method=payment_method
        )

        # Add new order to the database
        db.session.add(new_order)
        db.session.commit()

        # Create order items
        for item in cart_items:
            order_item = OrderItem(
                product_name=item['Dres_type'],
                product_price=item['price_of_a_dress'],
                quantity=item['quantity'],
                order_id=new_order.id
            )
            db.session.add(order_item)

        db.session.commit()
        order_details = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'address': address_line_1,
            'city': city,
            'state': state,
            'postalcode': postalcode,
            'phone': phone,
            'total_price': request.form['total_price'],
            'cart_items': cart_items  # This should be fetched based on your cart logic
        }
        send_order_confirmation_email(order_details['email'], order_details)
        flash(
            'Your order has been placed and a confirmation email has been sent.', 'success')
        return redirect(url_for('order_confirmation'))

    # If method is GET, render checkout page with cart details
    cart_items = session.get('cart', [])
    total_price = sum(item['price_of_a_dress'] * item['quantity']
                      for item in cart_items) + 20

    return render_template('checkout.html', cart_items=cart_items, total_price=total_price, get_dress_by_id=get_dress_by_id)


@app.route("/home")
def home():
    username = session.get('username')
    return render_template("home.html", username=username)


@app.route("/renting_process")
def renting_process():
    return render_template("renting_process.html")


@app.route("/lender_form", methods=["GET", "POST"])
def lender_form():
    if request.method == "POST":
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        phone = request.form.get("phone")
        email = request.form.get("email")
        lender_city = request.form.get("lender_city")
        Dres_type = request.form.get("Dres_type")
        other_lender_city = request.form.get("other_lender_city")
        price_of_a_dress = request.form.get("price_of_a_dress")
        Brand = request.form.get("Brand")
        Size = request.form.get("Size")
        date_of_purchase = request.form.get("date_of_purchase")
        dress_info = request.form.get("dress_info")
        image = request.files['image'].read()

        form_data = LenderForm(
            fname=fname,
            lname=lname,
            phone=phone,
            email=email,
            lender_city=lender_city,
            Dres_type=Dres_type,
            other_lender_city=other_lender_city,
            price_of_a_dress=price_of_a_dress,
            Brand=Brand,
            Size=Size,
            date_of_purchase=date_of_purchase,
            dress_info=dress_info,
            image=image
        )

        db.session.add(form_data)
        db.session.commit()

        flash('Your Data has been successfully inserted.', 'success')
        return render_template("lender_form.html")
    else:
        return render_template("lender_form.html")


@app.route("/lender_data")
def lender_data():
    lender_data = LenderForm.query.all()
    for form_data in lender_data:
        form_data.image_base64 = base64.b64encode(
            form_data.image).decode('utf-8') if form_data.image else None
    return render_template("lender_data.html", lenders_data=lender_data)


@app.route("/mahndi_dresses")
def mahndi_dresses():
    mahndi_dresses = LenderForm.query.filter_by(Dres_type="Mahndi").all()
    for dress in mahndi_dresses:
        dress.image_base64 = base64.b64encode(
            dress.image).decode('utf-8') if dress.image else None
    return render_template("mahndi_dresses.html", mahndi_dresses=mahndi_dresses)


@app.route("/valima_dresses")
def valima_dresses():
    valima_dresses = LenderForm.query.filter_by(Dres_type="Valima").all()
    for dress in valima_dresses:
        dress.image_base64 = base64.b64encode(
            dress.image).decode('utf-8') if dress.image else None
    return render_template("valima_dresses.html", valima_dresses=valima_dresses)


@app.route("/nikkah_dresses")
def nikkah_dresses():
    nikkah_dresses = LenderForm.query.filter_by(Dres_type="Nikkah").all()
    for dress in nikkah_dresses:
        dress.image_base64 = base64.b64encode(
            dress.image).decode('utf-8') if dress.image else None
    return render_template("Nikkah.html", Nikkah_dresses=nikkah_dresses)


@app.route("/baraat_dresses")
def baraat_dresses():
    baraat_dresses = LenderForm.query.filter_by(Dres_type="Baraat").all()
    for dress in baraat_dresses:
        dress.image_base64 = base64.b64encode(
            dress.image).decode('utf-8') if dress.image else None
    return render_template("Baraat_dresses.html", Baraat_dresses=baraat_dresses)


@app.route("/sarees")
def sarees():
    Sarees_dress = LenderForm.query.filter_by(Dres_type="Saree").all()
    for dress in Sarees_dress:
        dress.image_base64 = base64.b64encode(
            dress.image).decode('utf-8') if dress.image else None
    return render_template('sarees.html', Sarees_dress=Sarees_dress)


@app.route("/lehnga")
def lehnga():
    lehnga_dreses = LenderForm.query.filter_by(Dres_type="Lehnga").all()
    for dress in lehnga_dreses:
        dress.image_base64 = base64.b64encode(
            dress.image).decode('utf-8') if dress.image else None
    return render_template('Lehnga.html', Lehnga_dresses=lehnga_dreses)


@app.route("/gharas")
def gharas():
    gharas_dresses = LenderForm.query.filter_by(Dres_type="Gharas").all()
    for dress in gharas_dresses:
        dress.image_base64 = base64.b64encode(
            dress.image).decode('utf-8') if dress.image else None
    return render_template('gharas.html', Gharas_dresses=gharas_dresses)


@app.route("/other_dresses")
def other_dresses():
    other_dresses = LenderForm.query.filter_by(Dres_type="Other").all()
    for dress in other_dresses:
        dress.image_base64 = base64.b64encode(
            dress.image).decode('utf-8') if dress.image else None
    return render_template('other_dresses.html', Other_dresses=other_dresses)


@app.route("/dress_details/<int:dress_id>")
def dress_details(dress_id):
    dress = LenderForm.query.get(dress_id)
    if not dress:
        abort(404)
    image_base64 = base64.b64encode(dress.image).decode(
        'utf-8') if dress.image else None
    return render_template("dress_details.html", dress=dress, image_base64=image_base64)


def get_dress_by_id(dress_id):
    dress = LenderForm.query.get(dress_id)
    if not dress:
        abort(404)
    image_base64 = base64.b64encode(dress.image).decode(
        'utf-8') if dress.image else None
    return dress


@app.route('/add_to_cart/<int:dress_id>')
def add_to_cart(dress_id):
    dress = LenderForm.query.get(dress_id)

    if not dress:
        flash('Dress not found', 'danger')
        return redirect(url_for('lender_data'))

    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']
    for item in cart:
        if item['id'] == dress_id:
            item['quantity'] += 1
            break
    else:
        cart.append({
            'id': dress_id,
            'Dres_type': dress.Dres_type,
            'price_of_a_dress': dress.price_of_a_dress,
            'quantity': 1
        })

    session['cart'] = cart
    flash('Dress added to cart', 'success')
    return redirect(url_for('lender_data'))


@app.route('/remove_from_cart/<int:dress_id>')
def remove_from_cart(dress_id):
    cart = session.get('cart', [])
    session['cart'] = [item for item in cart if item['id'] != dress_id]
    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    if 'username' not in session:
        flash("You need to be logged in to view your cart.", "warning")
        return redirect(url_for('login'))

    cart = session.get('cart', [])
    total_price = sum(item['price_of_a_dress'] *
                      item['quantity'] for item in cart)
    print(total_price)
    return render_template('cart.html', cart=cart, total_price=total_price, get_dress_by_id=get_dress_by_id)


@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('cart'))


@app.route("/order_confirmation", methods=["GET", "POST"])
def order_confirmation():
    session.pop('cart', None)
    return render_template("order_confirmation.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        feedback = Feedback(name=name, email=email, message=message)
        db.session.add(feedback)
        db.session.commit()
        flash('Thanks for your message', 'success')
        return render_template("contact.html")
    else:
        return render_template("contact.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", debug=True)
