from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import random

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
    
@app.route("/delete/all", methods=["POST"])
def delete_all_players():
    try:
        db.session.query(Dart).delete()
        db.session.commit()
        return redirect("/")
    except:
        return "There was a problem with deleting all entries"
@app.route("/toggle_presence/<int:id>", methods=["POST"])
def toggle_presence(id):
    player = Dart.query.get_or_404(id)
    try:
        player.present = not player.present
        db.session.commit()
        return redirect("/")
    except:
        return "We could not set this player to ready"

    
@app.route("/start_game", methods=["GET","POST"])
def start_game():
    numbers = []
    present_players = Dart.query.filter_by(present=True).count()

    #find all valid divisors of present_players (ignoring 0)
    for i in range(2, present_players):
        if present_players % i == 0:
            numbers.append(i)
    
    return render_template("start_game.html",present_players=present_players, numbers = numbers)

@app.route("/game/<int:number_of_groups>", methods=["GET"])
def game(number_of_groups):
    #get all present players
    present_players = Dart.query.filter_by(present=True).all()
    player_names = [player.player for player in present_players]

    # Shuffle players and create groups
    random.shuffle(player_names)
    
    # Calculate number of players per group
    players_per_group = len(player_names) // number_of_groups
    groups = []
    
    for i in range(number_of_groups):
        # Create a group and append to groups list
        group = player_names[i * players_per_group: (i + 1) * players_per_group]
        groups.append(group)

    return render_template("groups.html", groups=groups, number_of_groups=number_of_groups)

@app.route("/randomize/<int:number_of_groups>", methods=["POST"])
def randomize_groups(number_of_groups):
    return redirect(url_for("game", number_of_groups=number_of_groups))

# This part is for the first game logic (group battles)
# Note: Databases for the group battle (überarbeiten)
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    players = db.relationship('GroupPlayer', backref='group', lazy=True)

    def __repr__(self):
        return f"<Group {self.name}>"

class GroupPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('dart.id'), nullable=False)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<GroupPlayer Player ID: {self.player_id} Group ID: {self.group_id}>"

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey('dart.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('dart.id'), nullable=False)
    winner_id = db.Column(db.Integer, db.ForeignKey('dart.id'), nullable=True)  # Nullable until a winner is declared
    match_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Match {self.id} between {self.player1_id} and {self.player2_id}>"


# note: i have to input the single groups in the function to add them to the db
@app.route("/game/savegroups", methods=["POST"])
def save_groups_to_db():
    pass



if __name__ == '__main__':
    app.run(debug=True)
