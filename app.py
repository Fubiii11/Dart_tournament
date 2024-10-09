import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config import get_secret_key
import pytz
import random

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config['SECRET_KEY'] = get_secret_key()

db = SQLAlchemy(app)

# Define the databases
class Dart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    present = db.Column(db.Boolean,default=False)

    def __repr__(self):
        return "<Player %r>" % self.player

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    players = db.relationship('GroupPlayer', backref='group', lazy=True)
    matches = db.relationship('Match', backref='group', lazy=True)
    def __repr__(self):
        return f"<Group {self.name}>"
    
class GroupPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('dart.id'), nullable=False)
    dart = db.relationship('Dart', backref='group_players')  # Access Dart model
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<GroupPlayer Player ID: {self.player_id} Group ID: {self.group_id}>"

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey('dart.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('dart.id'), nullable=False)
    winner_id = db.Column(db.Integer, db.ForeignKey('dart.id'), nullable=True)

    def __repr__(self):
        return f"<Match {self.id} between {self.player1_id} and {self.player2_id}>"

# Check if the database exists and create it if not
def create_db_if_not_exists():
    if not os.path.exists('test.db'):
        with app.app_context():
            db.create_all()  # Create all tables
            print("Database created.")

create_db_if_not_exists()  # Call this function only once when starting the app

# Function to convert UTC to Zurich time
def convert_utc_to_zurich(utc_dt):
    zurich_tz = pytz.timezone('Europe/Zurich')  # Define the Zurich timezone
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(zurich_tz)  # Convert to Zurich timezone

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

    session["groups"] = groups

    return render_template("groups.html", groups=groups, number_of_groups=number_of_groups)

@app.route("/randomize/<int:number_of_groups>", methods=["POST"])
def randomize_groups(number_of_groups):
    return redirect(url_for("game", number_of_groups=number_of_groups))

# note: i have to input the single groups in the function to add them to the db
@app.route("/game/savegroups", methods=["POST"])
def save_groups_to_db():
    GroupPlayer.query.delete()
    Group.query.delete()
    db.session.commit()

    groups = session.get("groups", [])

    for group_index, group_players in enumerate(groups):
        group_name = f"Group {group_index + 1}"
        group = Group(name=group_name)
        db.session.add(group)
        db.session.commit()  # Commit group to generate its ID

        # add players to the db
        for player_name in group_players:
            player = Dart.query.filter_by(player=player_name).first()
            if player:
                group_player = GroupPlayer(group_id=group.id, player_id=player.id)
                db.session.add(group_player)

    db.session.commit()
    
    # Create matches after saving groups
    create_matches_for_groups()

    groups = Group.query.all() 
    return render_template("elimination_round.html", group=groups)


def create_matches_for_groups():
    groups = Group.query.all()
    
    for group in groups:
        players = [gp.player_id for gp in group.players]
        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                match = Match(group_id=group.id, player1_id=players[i], player2_id=players[j])
                db.session.add(match)
    db.session.commit()

@app.route("/game/result", methods=["POST"])
def record_result():
    match_id = request.form['match_id']
    winner_id = request.form['winner_id']  # This should be the player who won the match

    match = Match.query.get(match_id)
    if match:
        match.winner_id = winner_id
        db.session.commit()

        # Update wins and losses
        winner = GroupPlayer.query.filter_by(player_id=winner_id, group_id=match.group_id).first()
        loser = GroupPlayer.query.filter_by(player_id=match.player1_id if winner_id == match.player2_id else match.player2_id, group_id=match.group_id).first()
        
        if winner:
            winner.wins += 1
        if loser:
            loser.losses += 1      
        db.session.commit()
    return redirect(url_for('some_route'))  # Redirect to a route that shows updated matches

if __name__ == '__main__':
    app.run(debug=True)
