###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required, ValidationError # Here, too
from flask_sqlalchemy import SQLAlchemy
import config # Stores port and domain
import requests

## App setup code
app = Flask(__name__)
app.config['SECRET_KEY'] = "SUPER SECRET KEY"
app.debug = True

## All app.config values
#NOTE: handled in config.py

#NOTE: DB Config
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/kevinmr"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)

######################################
######## HELPER FXNS (If any) ########
######################################
def get_player_info(name_in):
    r = requests.get('http://data.nba.net/10s/prod/v1/2016/players.json')
    PLAYER_INFO = r.json()
    first_name, last_name = name_in.split(' ')
    players = PLAYER_INFO['league']['standard']
    for player in players:
        if player["firstName"].lower() == first_name.lower() and player["lastName"].lower() == last_name.lower():
            return player
    return False

def get_team_info(team_id):
    r = requests.get('http://data.nba.net/10s/prod/v1/2016/teams.json')
    TEAM_INFO = r.json()['league']['standard']
    for team in TEAM_INFO:
        if int(team['teamId']) == int(team_id):
            team_name = team['nickname']
            return team_name
    return False

def create_teams():
    r = requests.get('http://data.nba.net/10s/prod/v1/2016/teams.json')
    TEAM_INFO = r.json()['league']['standard']
    for team in TEAM_INFO:
        team = Team(
            name=team['nickname']
        )
        db.session.add(team)
    db.session.commit()

def create_allstars():
    r = requests.get('http://data.nba.net/10s/prod/v1/allstar/2016/AS_roster.json')
    all_players = r.json()['sportsContent']['roster'][0]['players']
    for team_id in all_players.keys():
        #iterates through 2 teams
        for player in all_players[team_id]:
            new_player = AllStar(
                name=player['displayName'],
                position=player['positionFull']
            )
            db.session.add(new_player)
    all_coaches = r.json()['sportsContent']['roster'][0]['coaches']['coach']
    for coach in all_coaches:
        new_coach = AllStarCoach(
            name=coach['fullName'],
            team_name=coach['teamName']
        )
        db.session.add(new_coach)
    db.session.commit()


##################
##### MODELS #####
##################
class Player(db.Model):
    __tablename__ = "player"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    rank = db.Column(db.Integer())
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)

    def __repr__(self):
        return "{}".format(self.name)

class AllStar(db.Model):
    __tablename__ = "allstar"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    position = db.Column(db.String(64))

    def __repr__(self):
        return "{}".format(self.name)

class AllStarCoach(db.Model):
    __tablename__ = "coach"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    team_name = db.Column(db.String(64))

    def __repr__(self):
        return "{}".format(self.name)


class Team(db.Model):
    __tablename__ = "team"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    players = db.relationship('Player', backref='team', lazy=True)

    def __repr__(self):
        return "{}".format(self.name)

###################
###### FORMS ######
###################

class PlayerForm(FlaskForm):
    name = StringField("Please enter a player name: ",validators=[Required()])
    rank = StringField("Add a ranking for the player: ",validators=[Required()])
    submit = SubmitField()

    def validate_name(form, field):
        if not get_player_info(field.data):
            raise ValidationError('This is not an NBA player!')

    def validate_rank(form, field):
        try:
            int(field.data)
        except ValueError:
            raise ValidationError('This is not a number!')

#######################
###### VIEW FXNS ######
#######################

@app.route('/', methods=['GET', 'POST'])
def index():
    form = PlayerForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    if form.validate_on_submit():
        name = form.name.data
        rank = form.rank.data
        if Player.query.filter_by(name=name).count():
            players = Player.query.all()
            return render_template('index.html',form=form, players=players)
        if get_player_info(name):
            team_id = get_player_info(name)['teamId'].split()[0]
            team_name = get_team_info(team_id)
            new_team = Team(
                name=team_name
            )
            new_player = Player(
                name=name,
                rank=rank,
                team=new_team
            )
            db.session.add(new_player)
            db.session.add(new_team)
            db.session.commit()
            return redirect(url_for('rankings'))

    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    players = Player.query.all()
    return render_template('index.html',form=form, players=players)


@app.route('/rankings')
def rankings():
    players = Player.query.order_by('rank').all()
    return render_template('rankings.html', players=players)


@app.route('/teams')
def teams():
    create_teams()
    teams = Team.query.all()
    return render_template('teams.html', teams=teams)


@app.route('/allstars')
def allstars():
    create_allstars()
    players = AllStar.query.all()
    coaches = AllStarCoach.query.all()
    return render_template('allstars.html', players=players, coaches=coaches)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', error=error), 404

## Code to run the application...

# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    # listen on external IPs
    app.run(host=config.env['host'], port=config.env['port'])
