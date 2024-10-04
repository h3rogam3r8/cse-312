from flask import Flask
from flask import render_template 
from flask_bootstrap import Bootstrap5 

# Create a flask instance
app = Flask(__name__)
bootstrap = Bootstrap5(app)
# Route and view function

@app.route('/')
def index():
    return render_template("html/index.html", title = "Home")

# Security issue fixed
@app.after_request
def add_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# Run the app once this file executes
if __name__ == "__main__":
    app.run(debug=True)