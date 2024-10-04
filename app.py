from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)

class Dart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Player %r>" % self.player
    
with app.app_context():
    db.create_all()

# Store the list of players in memory (eventually, you can store this in a database)
players = []

# Home page route
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
