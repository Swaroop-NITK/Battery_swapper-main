from click import pass_context
from flask import Flask,json,redirect, render_template,flash,request
from flask.globals import request,session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import VARCHAR
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user

from flask_mail import Mail
import json

# mydatabase connecction
local_server=True
app=Flask(__name__) 
app.secret_key="secretkey"

with open('config.json','r') as c:
    params=json.load(c)["params"]

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)

# this is for getting the unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return customer.query.get(int(user_id)) or dealer.query.get(int(user_id))

# app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/databasename'3306
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost:3307/battery_swap'
db=SQLAlchemy(app)

#creating db models
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))
 
class customer(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True)
    name=db.Column(db.String(40))
    dob=db.Column(db.String(1000))
    phone_number=db.Column(db.String(10),unique=True)

class dealer(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    centre_id=db.Column(db.String(20))
    email=db.Column(db.String(100))
    password=db.Column(db.String(1000))

class centre(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    centre_id=db.Column(db.String(20),unique=True)
    centre_name=db.Column(db.String(50))
    battery_a=db.Column(db.Integer)
    battery_b=db.Column(db.Integer)
    battery_c=db.Column(db.Integer)
    battery_d=db.Column(db.Integer)

class booking(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True)
    name=db.Column(db.String(40))
    type=db.Column(db.String(1))
    centre_id=db.Column(db.String(20))
    address=db.Column(db.String(50))
    phone=db.Column(db.String(12),unique=True)

@app.route("/")
def home():
    return render_template("index.html")



@app.route("/usersignup")
def usersignup():
    return render_template("usersignup.html")


@app.route("/alllogin")
def alllogin():
    return render_template("alllogin.html")

@app.route("/userlogin")
def userlogin():
    return render_template("userlogin.html")

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=="POST":
        email=request.form.get('email')
        name=request.form.get('name')
        dob=request.form.get('dob')
        phone_number=request.form.get('phone-number')
        # print(email,name,dob,phone_number)
        encpassword=generate_password_hash(dob)
        user=customer.query.filter_by(email=email).first()
        phone=customer.query.filter_by(phone_number=phone_number).first()
        if user or phone:
            flash("Email or phone number is already taken","warning")
            return render_template("usersignup.html")
        new_user=db.engine.execute(f"INSERT INTO `customer`(`email`,`name`,`dob`,`phone_number`) VALUES ('{email}','{name}','{encpassword}','{phone_number}')")
    
        flash("Signup Success, PLEASE LOGIN","success")
        return render_template("userlogin.html") 

    return render_template("usersignup.html")


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=="POST":
        email=request.form.get('email')
        dob=request.form.get('dob')
        user=customer.query.filter_by(email=email).first()
        if user and check_password_hash(user.dob,dob):
            login_user(user)
            flash("Login Success","info")
            return redirect('/swap')
        else:
            flash("Invalid Credentials","danger")
            return render_template("userlogin.html")


    return render_template("userlogin.html")

@app.route('/dealerlogin',methods=['POST','GET'])
def dealerlogin():
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=dealer.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","info")
            return render_template("dealerloginnext.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("dealerlogin.html")


    return render_template("dealerlogin.html")    

@app.route('/admin',methods=['POST','GET'])
def admin():
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        if(username==params['user'] and password==params['password']):
            session['user']=username
            flash("login success","info")
            return render_template("adddealer.html")
        else:
            flash("Invalid credentials","danger")    
            
    return render_template("admin.html")
  
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('alllogin'))

#@app.route("/dealerlogin")
#def dealerlogin():
#    return render_template("dealerlogin.html")


@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html") 

@app.route("/contactus")
def contactus():
    return render_template("contactus.html")

@app.route('/adddealer',methods=['POST','GET'])
def adddealer():

    if('user' in session and session['user']==params['user']):
       
      if request.method=="POST":
        centre_id=request.form.get('centre_id')
        email=request.form.get('email')
        password=request.form.get('password')
        encpassword=generate_password_hash(password)
        centre_id=centre_id.upper()
        emaildealer=dealer.query.filter_by(email=email).first()
        if emaildealer:
            flash("Email is already taken","warning")
            return render_template("adddealer.html")

        db.engine.execute(f"INSERT INTO `dealer`(`centre_id`,`email`,`password`) VALUES ('{centre_id}','{email}','{encpassword}')")
        
        mail.send_message('BATTERY SWAP',sender=params['gmail-user'],recipients=[email],body=f"Welcome, Thanks for contributing to the future\nYour Login credentials Are:\nEmail Address: {email}\nPassword: {password}\nCentre ID:{centre_id}\n\nDo not share your password\n\n\nThank you")

        flash("Dealer Added Successfully","info")
        return render_template("adddealer.html")

    else:
      flash("Login and try again", "warning")
      return render_template("adddealer.html")
    

# testing whether db is connected or not
@app.route("/test")
def test():
    try:
        a=customer.query.all()
        print(a)
        return f'MY DATABASE IS CONNECTED {a} '
    except Exception as e:
            print(e)
            return f'MY DATABASE IS NOT CONNECTED {e}'

@app.route("/logoutadmin")
def logoutadmin():
    session.pop('user')
    flash("You are logged out", "primary")
    return redirect('/admin')

@app.route("/addcentredata",methods=['POST','GET'])
def addcentredata():

    email=current_user.email
    posts=dealer.query.filter_by(email=email).first()
    code=posts.centre_id
    print(code)
    postsdata=centre.query.filter_by(centre_id=code).first()

    if request.method=="POST":
        centre_id=request.form.get('centre_id')
        centre_name=request.form.get('centre_name')
        battery_a=request.form.get('battery_a')
        battery_b=request.form.get('battery_b')
        battery_c=request.form.get('battery_c')
        battery_d=request.form.get('battery_d')
        centre_id=centre_id.upper()
        dealer_1=dealer.query.filter_by(centre_id=centre_id).first()
        centre_1=centre.query.filter_by(centre_id=centre_id).first()
        if centre_1:
            flash("Centre is added, You can update it","primary")
            return redirect("/addcentredata")
        if dealer_1:
            db.engine.execute(f"INSERT INTO `centre` (`centre_id`,`centre_name`,`battery_a`,`battery_b`,`battery_c`,`battery_d`) VALUES('{centre_id}','{centre_name}','{battery_a}','{battery_b}','{battery_c}','{battery_d}')")
            flash("Centre Added","primary")
        else:
            flash("Centre ID doesnt exist","warning")

    #return render_template("centredata.html",postsdata=postsdata)
    return render_template("centredata.html",postsdata=postsdata)

@app.route("/centre_edit/<string:id>",methods=['POST','GET'])
@login_required
def centre_edit(id):
    posts=centre.query.filter_by(id=id).first()

    if request.method=="POST":
        centre_id=request.form.get('centre_id')
        centre_name=request.form.get('centre_name')
        battery_a=request.form.get('battery_a')
        battery_b=request.form.get('battery_b')
        battery_c=request.form.get('battery_c')
        battery_d=request.form.get('battery_d')
        centre_id=centre_id.upper()
        db.engine.execute(f"UPDATE `centre` SET `centre_id`='{centre_id}',`centre_name`='{centre_name}',`battery_a`='{battery_a}',`battery_b`='{battery_b}',`battery_c`='{battery_c}',`battery_d`='{battery_d}' WHERE `centre`.`id`={id}")
        flash("Centre Updated","info")
        return redirect("/addcentredata")

    #posts=centre.query.filter_by(id=id).first()
    return render_template("centre_edit.html",posts=posts)

@app.route("/centre_delete/<string:id>",methods=['POST','GET'])
@login_required
def centre_delete(id):
    db.engine.execute(f"DELETE FROM `centre` WHERE `centre`.`id`={id}")
    flash("Data deleted","danger")
    return redirect("/addcentredata")

@app.route("/swap",methods=['POST','GET'])
@login_required
def swap():
    query=db.engine.execute(f"SELECT * FROM `centre` ")
    if request.method=="POST":
        email=request.form.get('email')
        name=request.form.get('name')
        type=request.form.get('type')
        centre_id=request.form.get('centre_id')
        address=request.form.get('address')
        phone=request.form.get('phone')
        check2=centre.query.filter_by(centre_id=centre_id).first()
        if not check2:
            flash("Centre Code not exist","warning")

        code=centre_id
        dbb=db.engine.execute(f"SELECT * FROM `centre` WHERE `centre`.`centre_id`='{code}' ")        
        type=type
        if type=="A":       
            for d in dbb:
                seat=d.battery_a
                print(seat)
                ar=centre.query.filter_by(centre_id=code).first()
                ar.battery_a=seat-1
                db.session.commit()
                
            
        elif type=="B":      
            for d in dbb:
                seat=d.battery_b
                print(seat)
                ar=centre.query.filter_by(centre_id=code).first()
                ar.battery_b=seat-1
                db.session.commit()

        elif type=="C":     
            for d in dbb:
                seat=d.battery_c
                print(seat)
                ar=centre.query.filter_by(centre_id=code).first()
                ar.battery_c=seat-1
                db.session.commit()

        elif type=="D": 
            for d in dbb:
                seat=d.battery_d
                print(seat)
                ar=centre.query.filter_by(centre_id=code).first()
                ar.battery_d=seat-1
                db.session.commit()
        else:
            pass

        check=centre.query.filter_by(centre_id=centre_id).first()
        if(seat>0 and check):
            res=booking(email=email,name=name,type=type,centre_id=centre_id,address=address,phone=phone)
            db.session.add(res)
            db.session.commit()
            flash("Swap Successful","success")
        else:
            flash("Something Went Wrong","danger")



        

    return render_template("batterybooking.html",query=query)

app.run(debug=True) 
