from flask import Flask,request,redirect,url_for # type: ignore
from flask import render_template  # type: ignore
from flask import make_response # type: ignore
from flask_bootstrap5 import Bootstrap # type: ignore
from pymongo import MongoClient #database # type: ignore
from flask_bcrypt import Bcrypt # type: ignore
import secrets, hashlib


# Database set up
mongo_client = MongoClient('mongo')
db = mongo_client["users_info"]
users = db["users"]
auth = db["auth"]

# Create a flask instance
app = Flask(__name__)
bootstrap = Bootstrap(app) # Route and view function

# Hash
bcrypt = Bcrypt(app)

# Routes for each restaurant : 
@app.route('/austin-kitchen')
def austin_kitchen():
    return render_template('html/menu/austin_kitchen.html')

@app.route('/chick-mex')
def chick_mex():
    return render_template('html/menu/chick_mex.html')

@app.route('/dancing-chopsticks')
def dancing_chopsticks():
    return render_template('html/menu/dancing_chopsticks.html')

@app.route('/la-rosa')
def la_rosa():
    return render_template('html/menu/la_rosa.html')

@app.route('/poke-factory')
def poke_factory():
    return render_template('html/menu/poke_factory.html')

@app.route('/young-chow')
def young_chow():
    return render_template('html/menu/young_chow.html')

@app.route('/bollywood-bistro')
def bollywood_bistro():
    return render_template('html/menu/bollywood_bistro.html')

@app.route('/subway')
def subway():
    return render_template('html/menu/subway.html')

@app.route('/kung-fu-tea')
def kung_fu_tea():
    return render_template('html/menu/kung_fu_tea.html')

@app.route('/')
def index():
    loggedIn = False
    username = None

    auth_token = request.cookies.get('auth_token')

    if auth_token:
        # hash the auth token in order to compare it to the stored hashed token 
        hasher = hashlib.sha256()
        hasher.update(auth_token.encode())
        token_hash = hasher.hexdigest()

        # check if the hashed token exists in the database 
        token_entry = auth.find_one({token_hash: {'$exists': True}})
        if token_entry:
            username = token_entry[token_hash] # get the corresponding username
            loggedIn = True 
    return render_template("html/index.html", title = "Home", loggedIn=loggedIn, username=username) # render the homepage with the loggedIn status and username

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = False
    already_an_user=False
    too_long=False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        #check_existing_user
        existing_user = users.find_one({"username": username})
        if existing_user:
            return render_template("html/register.html",already_an_user=True)
        
        if len(username) > 30 or len(password) > 30:
            return (render_template("html/register.html",too_long=True))
        
        #check if passwords match, if they do we proceed to store passwords in database
        if password == confirm_password:
            hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user = {'username': username, 'password': hash_password}
            users.insert_one(user)
            return redirect(url_for('login'))
        else:
            return render_template("html/register.html",error=True)
    return render_template("html/register.html", title = "Register")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = False
    loggedIn = False
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        found_user = users.find_one({"username": username})
        if found_user:
            hashed_password = found_user["password"]

            #Check if the submitted password matches the one stored in the database
            if bcrypt.check_password_hash(hashed_password, password):
                response = make_response(render_template("html/index.html", title = "Home", loggedIn=True, username=username)) # render the homepage with the loggedIn status and username

                #Generate the Authentication Token
                auth_token = secrets.token_hex(20) 
                hasher = hashlib.sha256()
                bytes = auth_token.encode()
                hasher.update(bytes)
                hex_hash = hasher.hexdigest() #Hashed Auth Token as a hexadecimal string


                token = {hex_hash: username} 
                auth.insert_one(token) #Store the Hashed Auth Token in a separate database along with its associated user
                response.set_cookie("auth_token", auth_token, max_age=3600, httponly=True) #Set Auth Token Cookie
                return response
        return render_template("html/login.html", error=True) 
    return render_template("html/login.html", title = "Login") 

@app.route('/logout')
def logout():
    auth_token = request.cookies.get('auth_token')
    if auth_token:
        # hash the auth token to find it in the database
        hasher = hashlib.sha256()
        hasher.update(auth_token.encode())
        token_hash = hasher.hexdigest()

        # remove the token from the database to invalidate it
        auth.delete_one({token_hash: {'$exists': True}})

    # create a response object to redirect the user to the home page
    response = make_response(redirect(url_for('index')))
    # remove the auth_token cookie by setting its expiration date in the past
    response.set_cookie('auth_token', '', expires=0)
    return response

# Security issue fixed
@app.after_request
def add_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# Run the app once this file executes
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
