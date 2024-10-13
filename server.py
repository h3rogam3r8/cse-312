from flask import Flask,request,redirect,url_for # type: ignore
from flask import render_template  # type: ignore
from flask_bootstrap5 import Bootstrap # type: ignore
from pymongo import MongoClient #database
from flask_bcrypt import Bcrypt
# Create a flask instance

#database set up
mongo_client = MongoClient('mongo')
db = mongo_client["users_info"]
users = db["users"]


app = Flask(__name__)
bootstrap = Bootstrap(app)
# Route and view function


#hash
bcrypt = Bcrypt(app)


@app.route('/')
def index():
    return render_template("html/index.html", title = "Home")

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = False
    already_an_user=False
    too_long=False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_passowrd = request.form['confirm_password']
        #check_existing_user
        existing_user = users.find_one({"username": username})
        if existing_user:
            return render_template("html/register.html",already_an_user=True)
        
        if len(username) > 30 or len(password) > 30:
            return (render_template("html/register.html",too_long=True))
        #check if passwords match, if they do we proceed to store passwords in database
        if password == confirm_passowrd:
         hash_password =  bcrypt.generate_password_hash(password).decode('utf-8')
         user = {'username': username, 'password': hash_password}
         users.insert_one(user)
         return redirect(url_for('login'))
        else:
            return render_template("html/register.html",error=True)
    return render_template("html/register.html", title = "Register")

@app.route('/login')
def login():
    return render_template("html/login.html", title = "Login")

# Security issue fixed
@app.after_request
def add_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# Run the app once this file executes
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
