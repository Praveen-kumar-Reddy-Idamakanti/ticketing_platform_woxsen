from flask import Flask,render_template,redirect,url_for,session,request,jsonify
from pymongo import MongoClient
from flask_session import Session
import os
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import Register

###Creating the database connection!!>>
client = MongoClient("mongodb://localhost:27017/")  # Use your MongoDB URI
db = client["Website_Registers"]
organizers_loggedIn_collection = db["login_for_organizers"]
users_loggedIn_collection = db["login_for_users"]



#assigining the app name and folder Paths>>
app=Flask(__name__,template_folder="C:/Users/prave/Desktop/hack_woxsen/venv/templates",static_folder="C:/Users/prave/Desktop/hack_woxsen/venv/static")

#Session Server Side settings
app.secret_key=os.getenv("FLASK_SECRET_KEY")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"  # Store session data in local files

login_manager=LoginManager()
login_manager.login_view="login"
login_manager.init_app(app)

Session(app)

@login_manager.user_loader
def load_user(email):
    user=users_loggedIn_collection.find_one({"email":email})
    if user:
        return Register(user)
    return None


@app.route("/login_for_users",methods=["get"])
def login_user_render():
    return render_template("login_users.html")


@app.route("/login_for_organizers",methods=["get"])
def login_organizer_render():
    return render_template("login_organizers.html")


@app.route("/submit_login_users",methods=["POST"])
def login_users():
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
    if not email or not password:#checks all fields are there or not
        return jsonify({'error':"All fileds are required!!"}),400
    
    if "@" not in email:#validates email
        return jsonify({'error':"Invalid Email format!!"}),400
    
    user=users_loggedIn_collection.find_one({"email":email})
  
    print(user)
    if not user:
        return jsonify({'error':"Email not  regitsered"})
    user_obj=Register(user)#convert to Register object
             
    if user:
        user_password=user["password"]
    if not  check_password_hash(user_password,password):
        return jsonify({'error':"password mismatch!!"})
    login_user(user_obj)#  This will now store the email as session ID and also login the user
    print("logged In user")
    return redirect("/home")

#check organizers validation
@app.route("/submit_login_organizers",methods=["POST"])
def login_organizers():
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
    if not email or not password:#checks all fields are there or not
        return jsonify({'error':"All fileds are required!!"}),400
    
    if "@" not in email:#validates email
        return jsonify({'error':"Invalid Email format!!"}),400
    
    organizers=organizers_loggedIn_collection.find_one({"email":email})
  
    print(organizers)
    if not organizers:
        return jsonify({'error':"Email not  regitsered"})
    organizers_obj=Register(organizers)#convert to Register object
             
    if organizers:
        organizers_password=organizers["password"]
    if not  check_password_hash(organizers_password,password):
        return jsonify({'error':"password mismatch!!"})
    login_user(organizers_obj)#  This will now store the email as session ID and also login the user
    print("logged In user")
    return redirect("/home_for_users")

@app.route("/register_for_user")
def register_render():
    return render_template("register_user.html")
@app.route("/submit_register_users",methods=["POST"])
def register_user():
    if request.method=="POST":
        full_name=request.form.get("full_name")
        email=request.form.get("email")
        password=request.form.get("password")
        confirm_password=request.form.get("confirm_password")
        
        if password!=confirm_password:
            return jsonify({'eroor':"password!=confirm_password"}),400
        hashed_password = generate_password_hash(password)
        if not full_name or not email or not password:#checks all fields are there or not
            return jsonify({'error':"All fileds are required!!"}),400
        
        if "@" not in email:#validates email
            return jsonify({'error':"Invalid Email format!!"}),400
        
        if len(password)<6:
            return jsonify({'error':"Password must be greater than 6 characters"}),400
        #checking user is already in collection?>>
        user=users_loggedIn_collection.find_one({"email":email})
       
        if user:
            return jsonify({'message': 'Email is already registered'}), 200
        
        try:
            new_user=users_loggedIn_collection.insert_one({
                "full_name":full_name,
                "email":email,
                "password":hashed_password
                })
            return redirect("/")
        except Exception as e:
            return jsonify({'error': f"Error occurred: {str(e)}"}), 500

    return jsonify({'error': "GET method not allowed!"}), 405

@app.route("/register_for_organizer")
def register_render_organizer():
    return render_template("register_organizer.html")


@app.route("/submit_register_organizers",methods=["POST"])
def register_organizer():
    if request.method=="POST":
        full_name=request.form.get("full_name")
        email=request.form.get("email")
        password=request.form.get("password")
        confirm_password=request.form.get("confirm_password")
        
        if password!=confirm_password:
            return jsonify({'eroor':"password!=confirm_password"}),400
        hashed_password = generate_password_hash(password)
        if not full_name or not email or not password:#checks all fields are there or not
            return jsonify({'error':"All fileds are required!!"}),400
        
        if "@" not in email:#validates email
            return jsonify({'error':"Invalid Email format!!"}),400
        
        if len(password)<6:
            return jsonify({'error':"Password must be greater than 6 characters"}),400
        #checking user is already in collection?>>
        organizer=organizers_loggedIn_collection.find_one({"email":email})
       
        if organizer:
            return jsonify({'message': 'Email is already registered'}), 200
        
        try:
            new_organizer=organizers_loggedIn_collection.insert_one({
                "full_name":full_name,
                "email":email,
                "password":hashed_password
                })
            return redirect("/")
        except Exception as e:
            return jsonify({'error': f"Error occurred: {str(e)}"}), 500

    return jsonify({'error': "GET method not allowed!"}), 405


@app.route("/home_for_users")
def home_user():
    print(current_user)
    return render_template("home_users.html")

@app.route("/home_for_oragnizers")
def home_organizer():
    print(current_user)
    return render_template("home_oragnizers.html")

@app.route("/")
def index():
    return render_template("index.html")

if __name__=="__main__":
    app.run(debug=True)