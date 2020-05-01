
from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

class cage_measurements (db.Model):
    id = db.Column('cage_meaurements_id', db.Integer, primary_key = True)
    datetime = db.Column(db.String(100))
    food = db.Column(db.Boolean)
    water = db.Column(db.Integer)
    type = db.Column(db.String(10))

    def __init__(self, datetime, food, water, type):
        self.datetime = datetime
        self.food = food
        self.water = water
        self.type = type














