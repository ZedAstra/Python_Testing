from peewee import Model, CharField, IntegerField
from models import db


class Club(Model):
    name = CharField(primary_key=True)
    email = CharField()
    points = IntegerField()

    class Meta:
        database = db


Club.create_table()
