from flask_mail import Message, Mail

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jco2024ppsc4@gmail.com'
app.config['MAIL_PASSWORD'] = 'marshadcs20-24'
mail = Mail(app)


def send_order_confirmation_email(user_email, order_details):
    msg = Message('Order Confirmation',
                  sender='jco2024ppsc4@gmail.com',
                  recipients=[user_email])
    msg.body = render_template(
        'order_confirmation_email.txt', order_details=order_details)
