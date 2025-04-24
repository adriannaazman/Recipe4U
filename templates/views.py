from flask import Blueprint, views

view = Blueprint('views',__name__)

@views.route('/') 
def home():
    return "<h1>test</h1>"

