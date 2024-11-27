from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize the database
db = SQLAlchemy()

# Here the players that are entered are saved
class Dart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    present = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<Player %r>" % self.player

# Those are the groups that get created randomly
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    players = db.relationship('GroupPlayer', backref='group', lazy=True)
    matches = db.relationship('Match', backref='group', lazy=True)

    def __repr__(self):
        return f"<Group {self.name}>"

# Here you can see which person is in which group and how many points this person has
class GroupPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('dart.id'), nullable=False)
    dart = db.relationship('Dart', backref='group_players')
    total_points = db.Column(db.Integer, default = None)

    def __repr__(self):
        return f"<GroupPlayer Player ID: {self.player_id} Group ID: {self.group_id}>"

# Here all the matches that need to be played are safed
class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey('dart.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('dart.id'), nullable=False)
    player1_points = db.Column(db.Integer, default = 0)
    player2_points = db.Column(db.Integer, default = 0)
    match_started = db.Column(db.Boolean, default = False)
    match_finished = db.Column (db.Boolean, default = False)

    # Relationships
    player1 = db.relationship('Dart', foreign_keys=[player1_id])
    player2 = db.relationship('Dart', foreign_keys=[player2_id])

    def __repr__(self):
        return f"<Match {self.id} between {self.player1_id} and {self.player2_id}>"





# This Part is for the double elimination bracket
    
# tracks the 16 players advancing to the tournament
class TournamentPlayer(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    player_name = db.Column(db.String(100), nullable=False)
    player_id = db.Column(db.Integer, unique=True, nullable=False)
    final_rank = db.Column(db.String(20), nullable=True)
    rank_order = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<TournamentPlayer {self.player_name} (ID: {self.player_id}) - Rank: {self.final_rank} - rank_order: {self.rank_order}>"

class TournamentMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bracket_number = db.Column(db.Integer, nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey('tournament_player.player_id'), nullable=True)
    player2_id = db.Column(db.Integer, db.ForeignKey('tournament_player.player_id'), nullable=True)
    player1_points = db.Column(db.Integer, default=0)
    player2_points = db.Column(db.Integer, default=0)
    winner_id = db.Column(db.Integer, db.ForeignKey('tournament_player.player_id'), nullable=True)  # The winner of the match
    match_finished = db.Column(db.Boolean, default=False)

    # relationships
    player1 = db.relationship('TournamentPlayer', foreign_keys=[player1_id])
    player2 = db.relationship('TournamentPlayer', foreign_keys=[player2_id])

    def __repr__(self):
        return f"<TournamentMatch Bracket {self.bracket_number} - {self.player1_id} vs {self.player2_id}>"
