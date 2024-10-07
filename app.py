from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)

class Dart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    present = db.Column(db.Boolean,default=False)

    def __repr__(self):
        return "<Player %r>" % self.player
    
# Function to convert UTC to Zurich time
def convert_utc_to_zurich(utc_dt):
    zurich_tz = pytz.timezone('Europe/Zurich')  # Define the Zurich timezone
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(zurich_tz)  # Convert to Zurich timezone

# This was to initially create the database    
#with app.app_context():
    #db.create_all()

# Home page route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        player_content = request.form["player"]
        new_player = Dart(player=player_content)

        try:
            db.session.add(new_player)
            db.session.commit()
            return redirect("/#bottom")
        
        except:
            return "There was an issue adding this player"

    else:
        players = Dart.query.order_by(Dart.date_created).all()
        for player in players:
            player.date_created = convert_utc_to_zurich(player.date_created)

        #count the players
        total_players = Dart.query.count()

        present_players = Dart.query.filter_by(present=True).count()



        return render_template("index.html", players=players, total_players=total_players, present_players=present_players)
    
@app.route("/delete/<int:id>", methods=["POST"])
def delete_player(id):
    player_to_delete = Dart.query.get_or_404(id)

    try:
        db.session.delete(player_to_delete)
        db.session.commit()
        return redirect("/")
    except:
        return "There was a problem deleting this player"
    
@app.route("/toggle_presence/<int:id>", methods=["POST"])
def toggle_presence(id):
    player = Dart.query.get_or_404(id)
    try:
        player.present = not player.present
        db.session.commit()
        return redirect("/")
    except:
        return "We could not set this player to ready"

    
@app.route("/start_game", methods=["GET"])
def start_game():
    present_players = Dart.query.filter_by(present=True).count()
    return render_template("start_game.html",present_players=present_players)

if __name__ == '__main__':
    app.run(debug=True)
