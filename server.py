from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
load_dotenv()
import os
import random
import smtplib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sign up forms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(250), nullable=False)
    last_name = db.Column(db.String(250), nullable=False)
    mobile_number = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    dob = db.Column(db.String(250), nullable=False)
    gender = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    account_numbers = db.Column(db.String(250), nullable=False)


db.create_all()

otp = ""
user_data = {}
list = {}
change_pass = {}

account_number = ""
for _ in range(12):
    num = random.randint(0, 9)
    account_number += str(num)

all_users = db.session.query(User).all()


@app.route("/", methods=["POST", "GET"])
def sign():
    global list
    if request.method == "POST":
        all_users = db.session.query(User).all()
        mail = request.form["email"]
        pwd = request.form["password"]
        for user in all_users:
            if mail in user.email:
                if user.email == mail and pwd == user.password:
                    list = user
                    return redirect(url_for('user'))
                else:
                    return render_template('sign in.html', mails=user.email, pwds=user.password,
                                           incorrect='Enter correct email or password.')
        else:
            return render_template('sign in.html', mails=user.email, pwds=user.password,
                                dne='email is not registed in our bank.')
    else:
        return render_template('sign in.html')



@app.route("/forgotpassword", methods=["POST","GET"])
def forgot_password():
    global change_pass
    if request.method == "POST":
        mail = request.form["email"]
        all_users = db.session.query(User).all()
        print(all_users)
        for user in all_users:
            print(user)
            if mail in user.email:
                change_pass = user
                import smtplib
                my_email = os.getenv("EMAIL")
                password = os.getenv("PASSWORD")
                global otp
                for _ in range(4):
                    num = random.randint(0, 9)
                    otp = otp + str(num)
                with smtplib.SMTP("smtp.gmail.com", 587, timeout=120) as connection:
                    connection.starttls()
                    connection.login(user=my_email, password=password)
                    connection.sendmail(from_addr=my_email, to_addrs=mail,
                                        msg=f"subject:OTP for lella's Idea Bank\n\n{otp} is the otp to change password.")
                return render_template('forgot-password.html', mail=mail)
        return render_template('forgot-password.html', dne="Email has not registered yet.")
    else:
        return render_template('forgot-password.html')


@app.route("/check", methods=["GET", "POST"])
def changepassword():
    return redirect(url_for('keep'))


@app.route("/keeppassword", methods=["GET", "POST"])
def keep():
    if request.method == "POST":
        mail = change_pass.email
        newpass = request.form["newpass"]
        confirmpass = request.form["confirmpass"]
        if newpass == confirmpass:
            change_user = User.query.filter_by(email=mail).first()
            change_user.password = newpass
            db.session.commit()
            return render_template("sucess.html")
        else:
            return render_template('change.html', match="Password does not match")
    else:
        return render_template('change.html')


@app.route("/dashboard")
def user():
    return render_template("dashboard.html", user=list)


@app.route("/signup", methods=["POST", "GET"])
def function():
    global user_data
    if request.method == "POST":
        first_name = request.form["fname"]
        last_name = request.form["lname"]
        number = request.form["mobile"]
        mail = request.form["email"]
        birth = request.form["birth"]
        gender = request.form["gender"]
        password = request.form["password"]
        cpassword = request.form["cpassword"]
        if password == cpassword:
            user_data = {
                "first_name": first_name,
                "last_name": last_name,
                "number": number,
                "email": mail,
                "dob": birth,
                "gender": gender,
                "password": password,
            }
            my_email = "teamtrinity213@gmail.com"
            password = "noneoftheabove"
            global otp
            for _ in range(4):
                num = random.randint(0, 9)
                otp = otp + str(num)
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=120) as connection:
                connection.starttls()
                connection.login(user=my_email, password=password)
                connection.sendmail(from_addr=my_email, to_addrs=mail,
                                    msg=f"subject:OTP for lella's Idea Bank\n\n{otp} is the otp to create an account in our bank.")
            return redirect(url_for('verify'))
        return render_template("sign up.html", password=password, cpassword=cpassword)
    else:
        return render_template('sign up.html')


@app.route("/verify", methods=["POST", "GET"])
def verify():
    if request.method == "POST":
        user_otp = request.form["otp"]
        if otp == user_otp:
            new_user = User(
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                mobile_number=user_data["number"],
                email=user_data["email"],
                dob=user_data["dob"],
                gender=user_data["gender"],
                password=user_data["password"],
                account_numbers=account_number
            )
            db.session.add(new_user)
            db.session.commit()
            return render_template("sucess.html")
        return render_template('otp.html', otp=otp, user_otp=user_otp)
    else:
        return render_template('otp.html')


if __name__ == "__main__":
    app.run(debug=True)
