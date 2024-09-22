from peewee import *
from models import db

class Competition(Model):
    name = CharField(primary_key=True)
    date = DateTimeField()
    numberOfPlaces = IntegerField()
    
    class Meta:
        database = db
Competition.create_table()