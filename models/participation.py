from peewee import Model, ForeignKeyField, IntegerField
from models import db, Competition, Club


class Participation(Model):
    club = ForeignKeyField(Club)
    competition = ForeignKeyField(Competition)
    contestants = IntegerField()

    class Meta:
        database = db


Participation.create_table()
