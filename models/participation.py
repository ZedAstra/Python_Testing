from peewee import *
from models import db
from models import Competition,Club

class Participation(Model):
    club = ForeignKeyField(Club)
    competition = ForeignKeyField(Competition,)
    contestants = IntegerField()
    
    class Meta:
        database = db
Participation.create_table()