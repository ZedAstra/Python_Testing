from datetime import datetime
import json
import sqlite3
from peewee import *
from flask import Flask,render_template,request,redirect,flash,url_for

db = SqliteDatabase('database.db')

class Club(Model):
    name = CharField(primary_key=True)
    email = CharField()
    points = IntegerField()
       
    class Meta:
        database = db
    
class Competition(Model):
    name = CharField(primary_key=True)
    date = DateTimeField()
    numberOfPlaces = IntegerField()
    
    class Meta:
        database = db

def setupDatabase():
    db.connect(reuse_if_open=True)
    db.create_tables([Club, Competition], safe=True)
setupDatabase()

def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        for club in listOfClubs:
            c = Club.create(name=club['name'], email=club['email'], points=int(club['points']))
            print(c.get_or_create())
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        for competition in listOfCompetitions:
            c = Competition.create(name=competition['name'], date=datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S"), numberOfPlaces=competition['numberOfPlaces'])
            c.get_or_create()
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

loadClubs()
loadCompetitions()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    clubs_trouves = [club for club in Club.select() if club.email == request.form['email']]
    competitions = Competition.select()
    if clubs_trouves:
        club = clubs_trouves[0]
        return render_template('welcome.html',club=club,competitions=competitions);
    else:
        club = None
        return render_template('index.html',club=club,error="No club found with this email")
    


@app.route('/book/<competition>/<club>')
def book(competition,club):
    competitions = Competition.select()
    foundClub = [c for c in Club.select() if c.name == club][0]
    foundCompetition = [c for c in competitions if c.name == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competitions = Competition.select()
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in Club.select() if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))

