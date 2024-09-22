from datetime import datetime, timedelta
import json
from urllib.request import Request
import uuid
from peewee import *
from flask import Flask,render_template,request,redirect,flash,url_for,Response
import models
from models.user import User


def setupDatabase():
    print()
setupDatabase()

def loadClubs():
    with open('clubs.json') as clubs:
        listOfClubs = json.load(clubs)['clubs']
        for club in listOfClubs:
            if models.Club.get_or_none(club['name']) == None:
                c = models.Club.get_or_create(name=club['name'], email=club['email'], points=int(club['points']))


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        for competition in listOfCompetitions:
            if models.Competition.get_or_none(competition['name']) == None:
                c = models.Competition.get_or_create(name=competition['name'], date=datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S"), numberOfPlaces=competition['numberOfPlaces'])


app = Flask(__name__)
app.secret_key = 'something_special'

loadClubs()
loadCompetitions()

@app.route('/', methods=["GET"])
def index():
    if check_cookie(request) == True:
        token = get_authentication_cookie(request).split("=")[1]
        q = models.User().select().where(User.token == uuid.UUID(token)).limit(1)
        if len(q) == 0:
            return render_template('index.html')
        else:
            club = q[0].linked_club
            competitions = models.Competition.select()
            redirect("/summary")
            return render_template('welcome.html',club=club,competitions=competitions)
        
    return render_template('index.html')

@app.route('/summary',methods=['GET','POST'])
def summary():
    competitions = models.Competition.select()
    print(request.form)
    if check_cookie(request) == True:
        if request.form.get('email'):
            q = models.Club().select().where(models.Club.email == request.form['email']).limit(1)
            if(len(q) == 0):
                flash("No club found with this email")
                return render_template('index.html')
            club = q[0]
            res = Response(render_template('welcome.html',club=club,competitions=competitions))
            res.headers["Set-Cookie"] = get_authentication_cookie(request)
            return res
        else:
            token = get_authentication_cookie(request).split("=")[1]
            q = models.User().select().where(models.User.token == uuid.UUID(token)).limit(1)
            if len(q) == 1:
                return render_template('welcome.html',club=q[0].linked_club,competitions=competitions)
            else:
                return render_template('index.html')
    else:
        clubs_trouves = [club for club in models.Club.select() if club.email == request.form['email']]
        if clubs_trouves:
            club = clubs_trouves[0]
            q = models.User().select().where(models.User.linked_club == request.form['email']).limit(1)
            if len(q) == 0:
                res = Response(render_template('welcome.html',club=club,competitions=competitions))
                res.headers["Set-Cookie"] = create_cookie(club)
                return res
            else:
                res = Response(render_template('welcome.html',club=club,competitions=competitions))
                res.headers["Set-Cookie"] = "authentication="+str(q[0].token)
                return res
        else:
            club = None
            flash("No club found with this email")
            return render_template('index.html',club=club)
    


@app.route('/book/<competition>/<club>')
def book(competition,club):
    if check_cookie(request) == False:
        flash("You need to be logged in to book a competition")
        return render_template('index.html')
    competitions = models.Competition.select()
    foundClub = [c for c in models.Club.select() if c.name == club][0]
    foundCompetition = [c for c in competitions if c.name == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competitions = models.Competition.select()
    competition: models.Competition = [c for c in competitions if c.name == request.form['competition']][0]
    if competition:
        club = [c for c in models.Club.select() if c.name == request.form['club']][0]
        placesRequired = int(request.form['places'])
        competition.numberOfPlaces = competition.numberOfPlaces-placesRequired
        competition.save()
        flash('Great-booking complete!')
        return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display

@app.route('/pointsdisplay', methods=['GET'])
def pointsDisplay():
    print(request.headers["Cookie"])
    resp = Response()
    return render_template('points.html', clubs=models.Club.select())


@app.route('/logout',methods=['GET', 'POST'])
def logout():
    res = Response(render_template('index.html'))
    res.headers.set("Set-Cookie", "authentication=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
    return res

def check_cookie(request: Request):
    if request.headers.get("Cookie"):
        cookie = request.headers["Cookie"]
        entries = cookie.split(";")
        for entry in entries:
            if entry.startswith("authentication="):
                token = entry.split("=")[1]
                q = models.User().select().where(User.token == uuid.UUID(token)).limit(1)
                if len(q) == 1:
                    user = q[0]
                    if user.valid_until > datetime.now():
                        return True
                    else:
                        user.delete_instance()
                        return False
                else:
                    return False
            else:
                return False
    else:
        return False
    
def create_cookie(club):
    time = datetime.now() + timedelta(days=1)
    user = User.create(token=uuid.uuid4(), valid_until=time,linked_club=club)
    return "authentication="+str(user.token)+"; expires="+time.strftime("%a, %d %b %Y %H:%M:%S GMT")

def get_authentication_cookie(request):
    cookie = request.headers["Cookie"]
    entries = cookie.split(";")
    for entry in entries:
        if entry.startswith("authentication="):
            return entry
    return None
