from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize the database
db = SQLAlchemy()

# Dart model
class Dart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    present = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<Player %r>" % self.player

# Group model
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    players = db.relationship('GroupPlayer', backref='group', lazy=True)
    matches = db.relationship('Match', backref='group', lazy=True)

    def __repr__(self):
        return f"<Group {self.name}>"

# GroupPlayer model
class GroupPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('dart.id'), nullable=False)
    dart = db.relationship('Dart', backref='group_players')
    total_points = db.Column(db.Integer, default = None)

    def __repr__(self):
        return f"<GroupPlayer Player ID: {self.player_id} Group ID: {self.group_id}>"

# Match model
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
