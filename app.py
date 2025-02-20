from flask import Flask,render_template,redirect,url_for,session,request,jsonify,flash
from pymongo import MongoClient
from flask_session import Session
import os
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import Register
from bson.objectid import ObjectId  # <<--Import ObjectId to handle MongoDB IDs-->>

###Creating the database connection!!>>
client = MongoClient("mongodb://localhost:27017/")  # Use your MongoDB URI

db = client["Website_Registers"] #stores regitrations of users and organizers
organizers_loggedIn_collection = db["login_for_organizers"]
users_loggedIn_collection = db["login_for_users"]

db = client["EventManagement"]#stores the events hostes by organizers 
events_collection = db["events"]

tickets_collection = db["tickets"]  


#assigining the app name and folder Paths>>
app=Flask(__name__,template_folder="C:/Users/prave/Desktop/hack_woxsen/venv/templates",static_folder="C:/Users/prave/Desktop/hack_woxsen/venv/static")



#Session Server Side settings
app.secret_key=os.getenv("FLASK_SECRET_KEY")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"  # Store session data in local files

login_manager=LoginManager()
login_manager.login_view="login_organizer_render"
login_manager.init_app(app)

Session(app)

@login_manager.user_loader#checks everytime when we used login
def load_user(email):
    user = users_loggedIn_collection.find_one({"email": email})
    if user:
        return Register(user)  # Returning user object
    
    organizer = organizers_loggedIn_collection.find_one({"email": email})
    if organizer:
        return Register(organizer)  # Returning organizer object
    
    return None  # If neither user nor organizer is found

#<<----------------------->


@app.route("/login_for_users",methods=["get"])
def login_user_render():
    return render_template("login_users.html")#renders login for users


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
    login_user(user_obj)#  This will  store the email as session ID and also login the user
    print("logged In user")
    return redirect("/home_for_user")


#<<----------------------->

@app.route("/login_for_organizers",methods=["get"])
def login_organizer_render():
    return render_template("login_organizers.html")

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
    return redirect("/home_for_organizers")



#<<----------------------->


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
            return redirect("/login_for_users")
        except Exception as e:
            return jsonify({'error': f"Error occurred: {str(e)}"}), 500

    return jsonify({'error': "GET method not allowed!"}), 405



#<<----------------------->


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
            return redirect("/login_for_organizers")
        except Exception as e:
            return jsonify({'error': f"Error occurred: {str(e)}"}), 500

    return jsonify({'error': "GET method not allowed!"}), 405


#<<----------------------->



@app.route("/home_for_users")
@login_required
def home_user():
    return render_template("home_for_user.html")


@app.route("/home_for_organizers")
@login_required
def home_organizer():
    return render_template("home_for_organizers.html")

@app.route("/")
def index():
    return render_template("index.html")

#<<----------------------->

@app.route("/logout_organizer")
@login_required  # checks only logged-in users can log out
def logout():
    logout_user()  # Logs out the current user
    session.clear()  # Clear  session data
    return redirect("/login_for_organizers")  # Redirect to login page

#<<----------------------->

@app.route("/manage_events")
@login_required
def manage_events():
    events = events_collection.find({"organizer_email": current_user.email})  # Fetch events created by the logged-in organizer from databse
    return render_template("manage_events.html", events=events)


# Route to handle event creation
@app.route("/create_event", methods=["POST"])
@login_required
def create_event():
    event_name = request.form.get("eventName")
    event_description = request.form.get("eventDescription")
    event_date = request.form.get("eventDate")
    event_location = request.form.get("eventLocation")

    if not event_name or not event_description or not event_date or not event_location:
        flash("All fields are required!", "error")
        return redirect(url_for("manage_events"))

    event_data = {
        "organizer_email": current_user.email,  # Associate event with the logged-in organizer
        "event_name": event_name,
        "event_description": event_description,
        "event_date": event_date,
        "event_location": event_location,
    }

    events_collection.insert_one(event_data)
    flash("Event created successfully!", "success")
    return redirect(url_for("manage_events"))


# Route to handle event deletion
@app.route("/delete_event/<event_id>", methods=["POST"])
@login_required
def delete_event(event_id):
    events_collection.delete_one({"_id": ObjectId(event_id)})
    flash("Event deleted successfully!", "success")
    return redirect(url_for("manage_events"))

#<<----------------------->>

@app.route("/organizer_profile")
@login_required
def organizer_profile():
    # Fetch the logged-in organizer's details
    organizer = organizers_loggedIn_collection.find_one({"email": current_user.email})

    # Fetch events created by this organizer
    events = list(events_collection.find({"organizer_email": current_user.email}))

    return render_template("organizer_profile.html", organizer=organizer, events=events)

#<<----------------------->>


@app.route("/ticket_sales")
def ticket():
    return render_template("ticket_sales.html")

@app.route("/get_tickets", methods=["GET"])
def get_tickets():
    tickets = []
    for ticket in tickets_collection.find():
        event = events_collection.find_one({"_id": ObjectId(ticket["event_id"])})
        tickets.append({
            "_id": str(ticket["_id"]),
            "name": ticket["name"],
            "email": ticket["email"],
            "event_name": event["name"] if event else "Unknown",
            "quantity": ticket["quantity"]
        })
    return jsonify(tickets)




if __name__=="__main__":
    app.run(debug=True)
