from flask import Flask, render_template, request, redirect, url_for
import random
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='amarpratapsingh8929@gmail.com',  # Replace with your email
    MAIL_PASSWORD='ivng vwmb prwf atua', # Replace with your app password
    MAIL_DEFAULT_SENDER='amarpratapsingh8929@gmail.com'
)

mail = Mail(app)  # Initialize Flask-Mail

# This dictionary will store OTPs associated with email addresses
otp_storage = {}
mail = Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/evc"
db = SQLAlchemy(app)
class User(db.Model):
    name = db.Column(db.String(32))
    mobile = db.Column(db.String(12))
    email = db.Column(db.String(32), primary_key=True)
    brand = db.Column(db.String(16))
    model = db.Column(db.String(12))
    vechile_number = db.Column(db.String(12))
    bc = db.Column(db.String(12))
    c_type = db.Column(db.String(12))
    username = db.Column(db.String(32))
    password = db.Column(db.String(16)),

class Contact(db.Model):
    s_no = db.Column(db.Integer(), primary_key = True)
    name = db.Column(db.String(32), nullable=False)
    vehicle_number = db.Column(db.String(12), nullable=False )
    message = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True, default=datetime.now), 

def calculate_charging_info(distance, battery_percentage):
    # Assume some calculations for charging information
    # You can replace this with your actual calculations
    actual = distance-(348*(battery_percentage/100))
    number_of_charges = actual/348
    price_to_use = 30 * number_of_charges * 5.5
    time_taken = distance * 0.0005556 + 4 * number_of_charges

    return number_of_charges, price_to_use, time_taken

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        distance = float(request.form['distance'])
        battery_percentage = float(request.form['battery'])

        number_of_charges, price_to_use, time_taken = calculate_charging_info(distance, battery_percentage)

        return render_template('plan.html', 
                               distance=distance, 
                               battery_percentage=battery_percentage,
                               number_of_charges=number_of_charges,
                               price_to_use=price_to_use,
                               time_taken=time_taken)
    return render_template('plan.html')

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if (request.method=='POST'):
        name = request.form.get('name')
        vnumber = request.form.get('vehicleNumber')
        msg = request.form.get('message')
        email = request.form.get('email')
        entry = Contact(name=name, vehicle_number=vnumber, message=msg)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name, sender=email, recipients=['amarpratapsingh8929@gmail.com'], body=msg + "\n" + vnumber)
    return render_template('helpline.html')

@app.route('/forget')
def forget_password():
    return render_template('forget_password.html')

@app.route('/send_otp', methods=['POST'])
def send_otp():
    email = request.form['email']
    # Generate a random 6-digit OTP
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    otp_storage[email] = otp  # Store OTP in the dictionary
    # Here you would send the OTP to the user's email
    msg = Message('OTP for ' + email, recipients=[email])
    msg.body = 'Your OTP is: ' + otp
    mail.send(msg)
    print("OTP for", email, "is:", otp)
    return redirect(url_for('verify_otp', email=email))

@app.route('/verify_otp')
def verify_otp():
    email = request.args.get('email')
    return render_template('verify_otp.html', email=email)

@app.route('/check_otp', methods=['POST'])
def check_otp():
    otp_entered = request.form['otp']
    email = request.form['email']
    stored_otp = otp_storage.get(email)
    if stored_otp == otp_entered:
        return redirect(url_for('update_password', email=email))
    else:
        return "Invalid OTP"

@app.route('/update_password', methods=['GET', 'POST'])
def update_password():
    if request.method == 'GET':
        email = request.args.get('email')
        return render_template('update_password.html', email=email)
    elif request.method == 'POST':
        email = request.form['email']
        new_password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = new_password
            db.session.commit()
            return "Password updated successfully!"
        else:
            return "User with email {} not found".format(email)
    else:
        return "Method not allowed"

if __name__ == '__main__':
    app.run(debug=True)
