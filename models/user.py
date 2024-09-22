import flask_login
from peewee import *
from models import db, Club


class User(Model):
    token = UUIDField(primary_key=True)
    valid_until = DateTimeField()
    linked_club = ForeignKeyField(Club)
    
    class Meta:
        database = db
User.create_table()