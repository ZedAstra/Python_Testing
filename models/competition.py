from peewee import Model, CharField, DateTimeField, IntegerField
from models import db


class Competition(Model):
    name = CharField(primary_key=True)
    date = DateTimeField()
    numberOfPlaces = IntegerField()

    class Meta:
        database = db


Competition.create_table()
