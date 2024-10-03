from datetime import datetime, timedelta
import json
from urllib.request import Request
import uuid
from peewee import *
from flask import Flask,render_template,request,redirect,flash,url_for,Response
import models
from models import Club,User,Competition


def setupDatabase():
    print()
setupDatabase()

def loadClubs():
    with open('clubs.json') as clubs:
        listOfClubs = json.load(clubs)['clubs']
        for club in listOfClubs:
            q = models.Club().select().where(models.Club.name == club['name'])
            if len(q) == 0:
                models.Club().create(name=club['name'], email=club['email'], points=int(club['points']))


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        for competition in listOfCompetitions:
            q = models.Competition().select().where(models.Competition.name == competition['name'])
            if len(q) == 0:
                models.Competition().create(name=competition['name'], date=datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S"), numberOfPlaces=competition['numberOfPlaces'])


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
            return redirect("/summary")
            #return render_template('welcome.html',club=club,competitions=competitions)
        
    return render_template('index.html')

@app.route('/summary',methods=['GET','POST'])
def summary():
    competitions = models.Competition.select()
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
        if request.form.get("email"):
            clubs_trouves = [club for club in models.Club.select() if club.email == request.form['email']]
            if clubs_trouves:
                club = clubs_trouves[0]
                q = models.User().select().where(models.User.linked_club == club).limit(1)
                if len(q) == 0:
                    res = Response(render_template('welcome.html',club=club,competitions=competitions))
                    res.headers["Set-Cookie"] = create_cookie(club)
                    return res
                else:
                    res = Response(render_template('welcome.html',club=club,competitions=competitions))
                    if q[0].valid_until < datetime.now():
                        q[0].delete()
                        res.headers["Set-Cookie"] = create_cookie(club)
                        return res
                    else:
                        res.headers["Set-Cookie"] = "authentication="+str(q[0].token)
                        return res
            else:
                club = None
                flash("No club found with this email")
                return render_template('index.html',club=club)
        else:
            return redirect("/")
    

@app.route('/book/<competition>/<club>')
def book(competition,club):
    if check_cookie(request) == False:
        flash("You need to be logged in to book a competition")
        return redirect(url_for('index'))
    competitions = models.Competition().select()
    q1 = models.Club().select().where(models.Club.name == club).limit(1)
    q2 = models.Competition().select().where(models.Competition.name == competition).limit(1)
    if len(q1) == 1 and len(q2) == 1:
        foundClub = q1[0]
        foundCompetition = q2[0]
        m = min(12, foundCompetition.numberOfPlaces)
        return render_template('booking.html',club=foundClub,competition=foundCompetition,max=m)
    else:
        flash("Something went wrong. Please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchaseplaces',methods=['POST'])
def purchasePlaces():
    competitions = models.Competition.select()
    q1 = (models.Competition()
            .select()
            .where(models.Competition.name == request.form.get("competition")))
    q2 = (models.Club()
            .select()
            .where(models.Club.name == request.form.get("club")))
    if len(q1) == 1 and len(q2) == 1:
        competition: Competition = q1[0]
        club: Club = q2[0]
        places = request.form.get('places')
        if places == '':
            places = "0"
        placesRequired = int(places)
        if placesRequired < 1:
            flash("You need to book at least one place")
            return redirect(request.full_url)
        if competition.numberOfPlaces < placesRequired:
            flash("Not enough places available")
            return redirect(request.full_url)
        if(club.points >= placesRequired):
            club.points = club.points-placesRequired
            club.save()
            competition.numberOfPlaces = competition.numberOfPlaces-placesRequired
            competition.save()
            q3 = (models.Participation()
                .select()
                .where(models.Participation.competition == competition, models.Participation.club == club))
            if len(q3) == 1:
                participation: models.Participation = q3[0]
                participation.contestants = participation.contestants + placesRequired
                participation.save()
            else:
                models.Participation.create(club=club, competition=competition, contestants=placesRequired)
            flash('Successfully booked ' + str(placesRequired) + 'place(s)!')
            return redirect(url_for("summary"))
        else:
            flash("Your club doesn't have enough points!")
            return redirect(url_for("summary"))


# TODO: Add route for points display

@app.route('/pointsdisplay', methods=['GET'])
def pointsDisplay():
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
