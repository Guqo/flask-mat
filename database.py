import sqlite3
from flask import g

def connect_to_database():
    sql = sqlite3.connect('C:/Users/ryto0/Desktop/flask-mat-main/flaskapp.db')
    sql.row_factory = sqlite3.Row
    return sql

def getDatabase():
    if not hasattr(g, "flaskapp_db"):
        g.flaskapp_db = connect_to_database()
    return g.flaskapp_db