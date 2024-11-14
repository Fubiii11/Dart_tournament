import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import pytz
import random
from config import get_secret_key
from databases import *   # Import the db and models note: change * maybe
from livereload import Server
from bracket_config import BRACKET_ADVANCEMENT

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config['SECRET_KEY'] = get_secret_key()

# Initialize the app with SQLAlchemy
db.init_app(app)

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
    
# note: delete this at the end just for testing
@app.route("/fill/test", methods=["POST"])
def fill_testcases():
    for i in range(1,25):
        player_content = "player" + str(i)
        new_player = Dart(player = player_content, present = True)
        try:
            db.session.add(new_player)    
            db.session.commit()
        except:
            return "did not work"
    return redirect("/")

@app.route("/start_game", methods=["GET","POST"])
def start_game():
    numbers = []
    present_players = Dart.query.filter_by(present=True).count()

    #find all valid divisors of present_players (ignoring 0)
    if present_players > 1:
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


@app.route("/game/savegroups", methods=["POST"])
def save_groups_to_db():
    GroupPlayer.query.delete()
    Group.query.delete()
    Match.query.delete()
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

    return redirect(url_for("show_elimination_round"))

@app.route("/elimination-round")
def show_elimination_round():
    groups = Group.query.all()
    matches = Match.query.all() 
    return render_template("elimination_round.html", groups = groups, matches = matches)


def create_matches_for_groups():
    groups = Group.query.all()
    
    for group in groups:
        players = [gp.player_id for gp in group.players]
        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                match = Match(group_id=group.id, player1_id=players[i], player2_id=players[j])
                db.session.add(match)
    db.session.commit()

@app.route("/elimination-round/points/<int:match_id>/<string:player>", methods=["POST"])
def point_handler(match_id, player):
    # Get the match by its ID
    match = Match.query.get_or_404(match_id)

    # Toggle points for player1 or player2
    if player == 'player1':
        if match.player1_points == 0 and match.player2_points != 2:
            match.player1_points = 1
            match.match_started = True
        elif match.player1_points == 1 and match.player2_points != 2:
            match.player1_points = 2
            match.match_started = False
            match.match_finished = True
        elif match.player1_points == 2:
            match.player1_points = 0
            match.match_finished = False 
            if match.player2_points == 1:
                match.match_started = True
    elif player == 'player2':
        if match.player2_points == 0 and match.player1_points != 2:
            match.player2_points = 1
            match.match_started = True
        elif match.player2_points == 1 and match.player1_points != 2:
            match.player2_points = 2
            match.match_started = False
            match.match_finished = True
        elif match.player2_points == 2:
            match.player2_points = 0
            match.match_finished = False
            if match.player1_points == 1:
                match.match_started = True
    # Save changes to db
    db.session.commit()

    #redirect back to the page
    return redirect("/elimination-round")

@app.route("/elimination-round/start/<int:match_id>", methods=["POST"])
def start_match(match_id):
    # Find the correct match using the match_id
    match = Match.query.get_or_404(match_id)
    if match.match_started == False:
        match.match_started = True
    else:
        match.match_started = False
    db.session.commit()

    return redirect("/elimination-round")

@app.route("/elimination-round/results", methods=["GET"])
def show_results():
    matches = Match.query.all()

    # Check if all matches are finished
    for match in matches:
        if not match.match_finished:
            # Flash an error message if any match is not finished
            flash("Not all matches are played or finished", "error")

            return redirect("/elimination-round")
    
    # calculate the points for each player
    group_players = GroupPlayer.query.all()

    # Reset total points before calculation
    for gp in group_players:
        gp.total_points = 0
    
    # Iterate through all matches and update total_points for the players that played
    for match in matches:
        if match.match_finished:
            # Upadte Player1 points
            player1_gp = GroupPlayer.query.filter_by(group_id = match.group_id, player_id = match.player1_id).first()
            if player1_gp:
                player1_gp.total_points += match.player1_points
            # Update Player2 points  
            player2_gp = GroupPlayer.query.filter_by(group_id = match.group_id, player_id = match.player2_id).first()
            if player2_gp:
                player2_gp.total_points += match.player2_points

    # commit the changes
    db.session.commit()

    leaderboard = Group.query.all()
    
    # Sort players inside each groups based on theyr points
    for group in leaderboard:
        group.players.sort(key=lambda p: p.total_points, reverse=True)
        print(f"Group {group.name}")
        for player in group.players:
            print(f"{player.dart.player} - {player.total_points}")

    # Get the players that are advancing
    advancing_players = get_players_for_next_round(leaderboard)
    
    # Render the leaderboard page if all matches are finished
    return render_template("first_leaderboard.html", leaderboard = leaderboard, advancing_players = advancing_players)

def get_players_for_next_round(groups):
    total_players_needed = 16
    num_groups = len(groups)
    
    # how many players from each group should advance
    players_per_groups = total_players_needed // num_groups
    remaining_players = total_players_needed % num_groups

    advancing_players = []

    # Select the players from each groups:
    for group in groups:
        # Add the 'player_per_group' players to the advancing list
        advancing_players.extend(group.players[:players_per_groups])

    # Handle the remaining players if there are any
    if remaining_players > 0:
        #Collect the next best player from each group
        potential_advancing_player = [group.players[players_per_groups] for group in groups if len(group.players) > players_per_groups]

        # Sort remaining players by total points and take the top ones based on 'remaining_players'
        potential_advancing_player.sort(key=lambda p: p.total_points, reverse=True)
        advancing_players.extend(potential_advancing_player[:remaining_players])
    
    return advancing_players

@app.route("/tournament/start", methods=["GET"])
def render_brackets():

    # Get the players that advance into the Tournament
    all_players = Group.query.all()
    advancing_players = get_players_for_next_round(all_players)

    # Put those players into the database
    assigne_tournament_player(advancing_players)
    # Initialize the brackets and fill the first ones
    initialize_matches()
    assign_fist_matches(advancing_players)
    matches = TournamentMatch.query.all()

    return render_template("double_elimination.html", matches = matches)

@app.route("/elimination-round/return", methods=["GET"])
def return_to_scoreboard():
    return redirect(url_for("show_elimination_round"))


# This is to initialize the tournament matches
def assigne_tournament_player(players):
    # Make sure there are no entries in the db
    # note: think about a abck button but i would not
    TournamentMatch.query.delete()
    TournamentPlayer.query.delete()
    db.session.commit()

    for player in players:
        dbplayer = TournamentPlayer(
            player_name=player.dart.player, # get the player name from the dart db
            player_id=player.player_id,     # get the players id
        )
        db.session.add(dbplayer)
    db.session.commit()

def initialize_matches():
    for bracket_num in range(1, 32):
        match = TournamentMatch(bracket_number=bracket_num)
        db.session.add(match)
    db.session.commit()

def assign_fist_matches(players):
    for i in range(8):
        #select matches 1-8 and assige the players
        match = TournamentMatch.query.filter_by(bracket_number = i + 1).first()
        match.player1_id = players[2 * i].player_id # Assigne player1
        match.player2_id = players[2 * i + 1].player_id # Assigne player2
        db.session.commit()

@app.route("/update_score/<int:bracket_number>/<string:player>", methods=["POST"])
def point_and_bracket_handler(bracket_number, player):
    match = TournamentMatch.query.filter_by(bracket_number=bracket_number).first_or_404()

    if player == 'player1':
        if match.player1_points == 2:
            match.player1_points = 0  # Reset if max score reached
            db.session.commit()
            
        elif match.player1_points < 2 and match.player2_points != 2:
            match.player1_points += 1
            db.session.commit()

        # check if 2 points have been reached by player1 (player1 won)
        if match.player1_points == 2:            
            #Logic to write the player to his new bracket
            match.winner_id = match.player1_id
            match.match_finished = True
            bracket_advance(match, 'player1')
            

    elif player == 'player2':
        if match.player2_points == 2:
            match.player2_points = 0  # Reset if max score reached
            db.session.commit()
        elif match.player2_points < 2 and match.player1_points != 2:
            match.player2_points += 1
            db.session.commit()
        
        # check if 2 points have been reached by player2
        if match.player2_points == 2:
            #Logic to write the player to his new bracket
            match.winner_id = match.player2_id
            match.match_finished = True
            bracket_advance(match, 'player2')

    # Save changes to db
    db.session.commit()

    # check if the game is finished and display the leaderboard
    champion = TournamentPlayer.query.filter_by(final_rank = 1).first()
    runner_up = TournamentPlayer.query.filter_by(final_rank = 2).first()

    if champion and runner_up:
        leaderboard_data = TournamentPlayer.query.order_by(TournamentPlayer.final_rank).all()
        return render_template('leaderboard.html', leaderboard=leaderboard_data)

    # Redirect back to the page if the game is not yet finished
    return redirect("/tournament/start2")

@app.route("/tournament/start2", methods = ["GET"])
def get_back_to_page():
    matches = TournamentMatch.query.all()
    return render_template("double_elimination.html", matches = matches )

# Handle how the players advance to the next match
def bracket_advance(match, winner):
    bracket_info = BRACKET_ADVANCEMENT.get(match.bracket_number)
    if not bracket_info:
        return  # No further brackets to advance

    # Determine winner and loser IDs based on who won
    if winner == 'player1':
        winner_id = match.player1_id
        loser_id = match.player2_id
    else:
        winner_id = match.player2_id
        loser_id = match.player1_id

    # Update winner int he match records
    # note: might be unnecessary i have to check if i even use this else i could save data
    match.winner_id = winner_id
    match.match_finished = True

    # Handle special cases for the final matches
    # If the match is 30 (last or second last match)
    if match.bracket_number == 30:
        if winner == "player1":
            # The game is finished player2 lost twice
            TournamentPlayer.query.filter_by(player_id=loser_id).update({"final_rank": 2})
            TournamentPlayer.query.filter_by(player_id=winner_id).update({"final_rank": 1})
            db.session.commit()
            return
            #if player2 won nothing happens and the player are getting written to the next bracket
    
    # if there is a second match beeing played
    elif match.bracket_number == 31:
        #player1 won the tournament player2 is second
        TournamentPlayer.query.filter_by(player_id=winner_id).update({"final_rank": 1})
        TournamentPlayer.query.filter_by(player_id=loser_id).update({"final_rank": 2})
        db.session.commit()
        return

    # Place the winner in the specified bracket and slot
    winner_bracket = bracket_info["winner"]["bracket"]
    winner_slot = bracket_info["winner"]["slot"]
    winner_match = TournamentMatch.query.filter_by(bracket_number=winner_bracket).first()
                 
    if winner_match:
        if winner_slot == "player1" and winner_match.player1_id is None:
            winner_match.player1_id = winner_id
        elif winner_slot == "player2" and winner_match.player2_id is None:
            winner_match.player2_id = winner_id
    else:
        return

    # Place the loser in the specified bracket and slot (if there is a losers' bracket)
    loser_bracket_info = bracket_info.get("loser")
    if loser_bracket_info:
        loser_bracket = loser_bracket_info["bracket"]
        loser_slot = loser_bracket_info["slot"]
        final_rank = bracket_info["final_rank"]
        loser_match = TournamentMatch.query.filter_by(bracket_number=loser_bracket).first()
        if final_rank:
            TournamentPlayer.query.filter_by(player_id=loser_id).update({"final_rank": final_rank})
            db.session.commit()
        elif loser_match:
            if loser_slot == "player1" and loser_match.player1_id is None:
                loser_match.player1_id = loser_id
            elif loser_slot == "player2" and loser_match.player2_id is None:
                loser_match.player2_id = loser_id
            

    db.session.commit()

    # still need to add the final rank and what happens if a player
    # doesent advance because they lost or even won the whole thing

if __name__ == '__main__':
    #app.run(debug=True)
    server = Server(app.wsgi_app)  # Use livereload's Server
    server.serve(port=5000, host='127.0.0.1')


'''
 notes:

The groups page should not shuffle when the page is reloaded
just if the shuffle button is pressed

look into the players counter. if two or more players have the same points
how is it decided who of them continues??

BIG MISTAKE:: total points are the matches they won not the points they made

The players in the matches that are already finished can still change theyr score

'''