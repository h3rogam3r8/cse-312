from flask import Flask # type: ignore
from flask import render_template  # type: ignore
from flask_bootstrap5 import Bootstrap # type: ignore

# Create a flask instance
app = Flask(__name__)
bootstrap = Bootstrap(app)
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
    app.run(host='0.0.0.0', port=8080, debug=True)
