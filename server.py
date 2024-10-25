from flask import Flask,redirect,url_for, jsonify ,request,flash# type: ignore
from flask import render_template  # type: ignore
from flask import make_response # type: ignore
from flask_bootstrap5 import Bootstrap # type: ignore
from pymongo import MongoClient #database # type: ignore
from flask_bcrypt import Bcrypt # type: ignore
import secrets, hashlib
from bson.objectid import ObjectId
import secrets
import html


# Database set up
mongo_client = MongoClient('mongo')
db = mongo_client["users_info"]
users = db["users"]
auth = db["auth"]
comments = db["comments"]

# Create a flask instance
app = Flask(__name__)
bootstrap = Bootstrap(app) # Route and view function


# Hash
bcrypt = Bcrypt(app)

# Routes for each restaurant : 
@app.route('/austin_kitchen')
def austin_kitchen():
    return restaurant_page("austin_kitchen")

@app.route('/chick_mex')
def chick_mex():
    return restaurant_page("chick_mex")

@app.route('/dancing_chopsticks')
def dancing_chopsticks():
    return restaurant_page("dancing_chopsticks")

@app.route('/la_rosa')
def la_rosa():
    return restaurant_page("la_rosa")

@app.route('/poke_factory')
def poke_factory():
    return restaurant_page("poke_factory")

@app.route('/young_chow')
def young_chow():
    return restaurant_page("young_chow")

@app.route('/bollywood_bistro')
def bollywood_bistro():
    return restaurant_page("bollywood_bistro")

@app.route('/subway')
def subway():
    return restaurant_page("subway")

@app.route('/kung_fu_tea')
def kung_fu_tea():
    
    return restaurant_page("kung_fu_tea")


def render_with_auth(template_name, **context):
    username = is_authenticated()  # get username if authenticated
    context['loggedIn'] = username is not None
    context['username'] = username
    return render_template(template_name, **context)

def is_authenticated():
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
      
            return username
        else:
            return None

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
        
        if len(username) > 30 or len(password) > 30 or len(password) < 9:
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
                response = make_response(redirect(url_for('index'))) # render the homepage with the loggedIn status and username
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
        return redirect(url_for('index',error=True)) 
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



@app.route('/<restaurant>', methods=['GET','POST'])
def restaurant_page(restaurant):
    # fetch restaurant details and comments
    
    all_comments = list(comments.find({"restaurant": restaurant}))  
    #print(all_comments)
    #escape_comments = html.escape(all_comments)
    return render_with_auth(
            f'html/menu/{restaurant}.html',
            comments=all_comments,
            restaurant_name=restaurant
        )

@app.route('/comment/<restaurant>', methods=['POST'])
def addcomment(restaurant):
        #restaurant = request.form.get('restaurant')
  
        user_comment = request.form.get('userComment')
        reply_comment = request.form.get('replyComment')
        comment_id = request.form.get('comment_id')
        auth_token = request.cookies.get('auth_token')

        username = None

        # Check if user is authenticated
        if auth_token:
         hasher = hashlib.sha256()
         hasher.update(auth_token.encode())
         token_hash = hasher.hexdigest()

         token_entry = auth.find_one({token_hash: {'$exists': True}})
         if token_entry:
            username = token_entry[token_hash]

        if not username:
            return redirect(url_for('login'))  # unauthenticated users to login

        if user_comment:  # check for a new comment
        
            #HTML escape
            #escape_comment = html.escape(user_comment)
            comments.insert_one({
            "restaurant": restaurant,
            "comment": user_comment,
            "username": username,
            "replies": []
            })
        elif reply_comment and comment_id:  # Check for a reply
            if username:  # Ensure the user is authenticated
            # Find the comment and update it with the new reply
            #HTML escape
                #escape_replycomment = html.escape(reply_comment)
                comments.update_one(
                {"_id": ObjectId(comment_id)},
                {"$push": {"replies": {"comment": reply_comment, "username": username}}}
                )
            else:
                return redirect(url_for('login'))  # Redirect to login if not authenticated
      
        return redirect(url_for('restaurant_page', restaurant=restaurant))
    
       

  
   
# Run the app once this file executes
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
