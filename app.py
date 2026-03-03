from flask import Flask
from models import db

app = Flask(__name__)

# SQLite configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

@app.route("/")
def home():
    return "Placement Portal Database Connected!"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # Creates all tables
    app.run(debug=True)