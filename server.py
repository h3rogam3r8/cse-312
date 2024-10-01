from flask import Flask 

# Create a flask instance 
app = Flask(__name__)

# Route and view function
@app.route('/')
def index():
    return 'Kris, Schindler!'

# Run the app once this file executes
if __name__ == "__main__":
    app.run(debug=True)