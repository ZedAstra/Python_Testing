from peewee import *

db = SqliteDatabase('database.db', pragmas={'foreign_keys': 2})