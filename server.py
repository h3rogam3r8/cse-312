from flask import Flask,redirect,url_for, jsonify ,request, flash, make_response, after_this_request # type: ignore
from flask import render_template  # type: ignore
from flask import make_response # type: ignore
from flask_bootstrap5 import Bootstrap # type: ignore
from pymongo import MongoClient #database # type: ignore
from flask_bcrypt import Bcrypt # type: ignore
import secrets, hashlib
from bson.objectid import ObjectId # type: ignore
import secrets
import html 
from werkzeug.utils import secure_filename  # type: ignore
import os
from flask import send_from_directory       # type: ignore
from os.path import join, dirname, realpath
import mimetypes
from flask_socketio import SocketIO, emit, join_room   # type: ignore
from flask_limiter import Limiter # type: ignore
from flask_limiter.util import get_remote_address # type: ignore
import uuid
import time

# Database set up
mongo_client = MongoClient('mongo')
db = mongo_client["users_info"]
users = db["users"]
auth = db["auth"]
comments = db["comments"]
reactions = db["reactions"]

CHAR_LIMIT = 280

user_cooldown = {}
COOLDOWN = 30

# Create a flask instance
app = Flask(__name__)
bootstrap = Bootstrap(app) # Route and view function
socketio = SocketIO(app, threaded=True)  # Set up SocketIO

# Create a limiter instance to limit the rate per user
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["50 per 10 seconds"],
)

# Hash
bcrypt = Bcrypt(app)

@app.errorhandler(429)
def ratelimit_handler(e):
    user_ip = get_remote_address()
    current_time = time.time()
    elapsed = 0
    new_cooldown = COOLDOWN
    if user_ip not in user_cooldown:
        user_cooldown[user_ip] = current_time
    else:
        prev_time = user_cooldown[user_ip]
        elapsed = current_time - prev_time
        new_cooldown = COOLDOWN - elapsed
        if new_cooldown > 0:
            user_cooldown[user_ip] = current_time
            return make_response(jsonify({"error": f"Whoaaa there, too many requests! Slow down! Please wait {str(new_cooldown)} seconds."}), 429)
        else:
            del user_cooldown[user_ip]
    return make_response(jsonify({"error": "Whoaaa there, too many requests! Slow down!"}), 429)

#for images upload
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit to 16MB
#checking for correct filetype
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        
        if len(username) > 30 or len(password) > 30 or len(password) < 8:
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
        return render_template("html/login.html",error=True)
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
    if restaurant != 'favicon':
        return render_with_auth(
                f'html/menu/{restaurant}.html',
                comments=all_comments,
                restaurant_name=restaurant
            )
    elif restaurant == 'favicon':
        return

# Changed this function to work with AJAX and always redirect to the same page
@app.route('/comment/<restaurant>', methods=['POST'])
def addcomment(restaurant):
        user_comment = request.form.get('userComment')
        reply_comment = request.form.get('replyComment')
        comment_id = request.form.get('comment_id')
        auth_token = request.cookies.get('auth_token')
        

        if user_comment and len(user_comment) > CHAR_LIMIT:
            return jsonify({'success': False,'error':'Comment too long'})
    
        if reply_comment and len(reply_comment) > CHAR_LIMIT:
            return jsonify({'success': False,'error':'Reply too long'})

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
            return jsonify({'success': False, 'error': 'Not authenticated'})
        
        image_url = None
        filename = None
        if 'image' in request.files:
         file = request.files['image']
         if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) 
            file.save(file_path)
            image_url = f'/uploads/{filename}'

        if user_comment and filename:  # check for a new comment
            comments.insert_one({
            "restaurant": restaurant,
            "comment": user_comment,
            "username": username,
            "image": filename, #storing image 
            "replies": []
            })
        elif user_comment:
            comments.insert_one({
            "restaurant": restaurant,
            "comment": user_comment,
            "username": username,
            "replies": []
            })
        
        elif reply_comment and comment_id:  # Check for a reply
            if username:  # Ensure the user is authenticated
                comments.update_one(
                {"_id": ObjectId(comment_id)},
                {"$push": {"replies": {"comment": reply_comment, "username": username}}}
                )
            else:
                return jsonify({'success': False, 'error': 'Not authenticated'})
      
        return jsonify({'success': True, 'imagePath': image_url})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/validate-length', methods=['POST'])
def validate_length():
    text = request.json.get('text', '')
    remaining = CHAR_LIMIT - len(text)
    return jsonify({'remaining': remaining, 'valid': remaining >= 0})

def broadcast_reaction_update(comment_id, likes, dislikes, like_usernames, dislike_usernames):
    socketio.emit('update_reaction_counts', {
        'comment_id': comment_id,
        'likes': likes,
        'dislikes': dislikes,
        'like_usernames': like_usernames,
        'dislike_usernames': dislike_usernames
    })

@app.route('/react/<string:comment_id>/<string:reaction_type>', methods=['POST'])
def handle_reaction(comment_id, reaction_type):
    auth_token = request.cookies.get('auth_token')
    hasher = hashlib.sha256()  # Get username from auth token

    # Guest functionality
    if hasher is None:
        return
    
    hasher.update(auth_token.encode())
    token_hash = hasher.hexdigest()
    token_entry = auth.find_one({token_hash: {'$exists': True}})
    
    username = token_entry[token_hash]
    
    # Check if user has already reacted
    existing_reaction = reactions.find_one({
        'comment_id': comment_id,
        'username': username
    })
    
    if existing_reaction:
        if existing_reaction['type'] == reaction_type:
            # Remove reaction if clicking same button
            reactions.delete_one({'_id': existing_reaction['_id']})
            reaction_counts = update_reaction_counts(comment_id).json
            broadcast_reaction_update(comment_id, reaction_counts['likes'], reaction_counts['dislikes'], reaction_counts['like_usernames'], reaction_counts['dislike_usernames'])
            return jsonify(reaction_counts)
        else:
            # Update reaction if changing from like to dislike or vice versa
            reactions.update_one(
                {'_id': existing_reaction['_id']},
                {'$set': {'type': reaction_type}}
            )
    else:
        # Create new reaction
        reactions.insert_one({
            'comment_id': comment_id,
            'username': username,
            'type': reaction_type
        })
    
    # Get updated counts and broadcast to all clients
    reaction_counts = update_reaction_counts(comment_id).json
    broadcast_reaction_update(comment_id, reaction_counts['likes'], reaction_counts['dislikes'], reaction_counts['like_usernames'], reaction_counts['dislike_usernames'])

    return jsonify(reaction_counts)

@app.route('/react/<string:comment_id>/count')
def update_reaction_counts(comment_id):
    likes = reactions.find({'comment_id': comment_id, 'type': 'like'})
    dislikes = reactions.find({'comment_id': comment_id, 'type': 'dislike'})
    
    like_usernames = []
    dislike_usernames = []

    for reaction in likes:
        like_usernames.append(reaction['username'])

    for reaction in dislikes:
        dislike_usernames.append(reaction['username'])

    return jsonify({
        'likes': len(like_usernames),
        'dislikes': len(dislike_usernames),
        'like_usernames': like_usernames,
        'dislike_usernames': dislike_usernames
    })

@app.route('/get-user-reaction/<string:comment_id>')
def get_user_reaction(comment_id):
    auth_token = request.cookies.get('auth_token')
    if not auth_token:
        return jsonify({'reaction': None})
    
    hasher = hashlib.sha256()
    hasher.update(auth_token.encode())
    token_hash = hasher.hexdigest()
    token_entry = auth.find_one({token_hash: {'$exists': True}})
    if not token_entry:
        return jsonify({'reaction': None})
    
    username = token_entry[token_hash]
    reaction = reactions.find_one({
        'comment_id': comment_id,
        'username': username
    })
    
    return jsonify({'reaction': reaction['type'] if reaction else None})
     


@app.before_request
def assign_user_id():
    user_id = request.cookies.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
        @after_this_request
        def set_cookie(response):
            response.set_cookie('user_id', user_id)
            return response
    request.user_id = user_id


active_polls = {}  # active polls

@app.route('/start_poll/<restaurant>', methods=['POST'])
def start_poll(restaurant):
    # removed authentication check to allow any user to start a poll (going to let any user interact with poll)

    if restaurant in active_polls:
        return jsonify({'success': False, 'error': 'A poll is already active for this restaurant.'}), 400

    dishes = request.json.get('dishes')
    if not dishes:
        return jsonify({'success': False, 'error': 'No dishes provided.'}), 400

    # set poll duration (60 seconds)
    poll_duration = 60
    end_time = time.time() + poll_duration

    # poll data
    poll = {
        'question': 'Which dish do you prefer?',
        'options': {dish: 0 for dish in dishes},
        'end_time': end_time,
        'votes': {}  
    }
    active_polls[restaurant] = poll

    # notification that the restaurant room that a new poll has started
    socketio.emit('poll_started', {
        'question': poll['question'],
        'options': poll['options'],
        'end_time': poll['end_time']
    }, room=restaurant)

    return jsonify({'success': True})


@app.route('/vote_poll/<restaurant>', methods=['POST'])
def vote_poll(restaurant):
    user_id = request.user_id

    if restaurant not in active_polls:
        return jsonify({'success': False, 'error': 'No active poll for this restaurant.'}), 400

    option = request.json.get('option')
    poll = active_polls[restaurant]

    # check if poll ended
    if time.time() >= poll['end_time']:
        del active_polls[restaurant]
        # notification that poll ended
        socketio.emit('poll_ended', {}, room=restaurant)
        return jsonify({'success': False, 'error': 'Poll has ended.'}), 400

    previous_vote = poll['votes'].get(user_id)
    if previous_vote:
        poll['options'][previous_vote] -= 1

    poll['votes'][user_id] = option
    poll['options'][option] += 1

    socketio.emit('poll_vote_update', {'options': poll['options']}, room=restaurant)

    return jsonify({'success': True})


@socketio.on('join_restaurant')
def on_join(data):
    restaurant = data['restaurant']
    join_room(restaurant)
    if restaurant in active_polls:
        poll = active_polls[restaurant]
        emit('poll_started', {
            'question': poll['question'],
            'options': poll['options'],
            'end_time': poll['end_time']
        }, room=request.sid)


def restaurant_page(restaurant):
    all_comments = list(comments.find({"restaurant": restaurant}))  

    # dishes for each restaurant
    dishes_dict = {
        'austin_kitchen': [
            'Bulgogi Over Rice',
            'Donkatsu',
            'Kimchi Bokkeumbap',
            'Spicy Pork Over Rice',
            'Soondooboo',
            'Pork Dumplings',
            'Kimchi Side'
        ],
        'bollywood_bistro': [
            'Chicken Biryani',
            'Chicken Kebab',
            'Chicken Samosa',
            'Garlic Naan',
            'Tandoori Chicken'
        ],
        'chick_mex': [
            'Burrito Bowl',
            'Chicken Over Rice',
            'Double Chicken Burger',
            'Fried Chicken',
            'Gyro',
            'Tacos'
        ],
        'dancing_chopsticks': [
            'Beef Teriyaki',
            'Chicken Katsu',
            'Chicken Yaki Udon',
            'Pork Katsu',
            'Tokyo Chicken',
            'Yakitori'
        ],
        'kung_fu_tea': [
            'Classic',
            'Milk Cap',
            'Milk Strike',
            'Milk Tea',
            'Punch',
            'Slush'
        ],
        'la_rosa': [
            'Buffalo Chicken Wings',
            'Cheese Pizza',
            'Pepperoni Pizza',
            'Garlic Knots',
            'Onion Rings',
            'French Fries'
        ],
        'poke_factory': [
            'Ahi Poke Bowl',
            'Salmon Poke Bowl',
            'Shrimp Poke Bowl',
            'Spicy Crab Poke Bowl',
            'Spicy Tuna Poke Bowl',
            'Teriyaki Chicken Poke Bowl'
        ],
        'subway': [
            'Steak and Bacon',
            'Chicken Rancher',
            'Cold Cut Combo',
            'Steak & Cheese',
            'Black Forest Ham',
            'Sweet Onion Chicken Teriyaki'
        ],
        'young_chow': [
            'Beef Lo Mein',
            'Hunan Chicken',
            'Hunan Shrimp',
            'Kung Pao Chicken',
            'Szechuan Beef',
            'Young Chow Fried Rice'
        ],
    }

    # Get the dishes for the current restaurant
    dishes = dishes_dict.get(restaurant, [])

    if restaurant != 'favicon':
        return render_with_auth(
            f'html/menu/{restaurant}.html',
            comments=all_comments,
            restaurant_name=restaurant,
            dishes=dishes
        )
    elif restaurant == 'favicon':
        return

# Run the app once this file executes
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
