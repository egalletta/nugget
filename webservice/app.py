import os
import time
import string
import random

import bcrypt
import flask_login
import requests
from flask import Flask, flash, redirect, render_template, request, url_for, abort, session
from flask_mongoengine import MongoEngine
from werkzeug.exceptions import NotFound
from nugget import Nugget, DiscoveredNugget
from user import User

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'nugget',
    'host': os.environ.get('MONGOSTR')
}
app.secret_key = os.environ.get('SECRET_KEY')
db = MongoEngine(app)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
WEATHER_API_KEY = os.environ.get('WEATHER_KEY')

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        lookup_user = User.objects(username=username).first()
        if lookup_user is not None and bcrypt.checkpw(password.encode('utf-8'), lookup_user.password.encode('utf-8')):
            flask_login.login_user(lookup_user)
            if 'url' in session:
                return redirect(session['url'])
            return redirect(url_for('home'))
        else:
            flash('Incorrect login information')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']
        if password != password2:
            flash('Passwords do not match')
            return url_for('register')
        lookup_user = User.objects(username=username).first()
        if lookup_user is None:
            new_user = User(username=username, password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()))
            new_user.save()
            flash('Successfully Registered; Please log in')
            return redirect(url_for('login'))
        else:
            flash("Username already taken")
            return redirect(url_for('register'))
    else:
        return render_template('register.html')

@app.route("/logout")
@flask_login.login_required
def logout():
    flask_login.logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/home', methods=['GET'])
def home():
    if not flask_login.current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        my_nuggets = Nugget.objects(assignee__iexact=flask_login.current_user.username)
        managed_nuggets = Nugget.objects(assigner__iexact=flask_login.current_user.username)
        return render_template('home.html', my_nuggets=my_nuggets, managed_nuggets=managed_nuggets)

@app.route('/motd', methods=['GET'])
def motd():
    mac = request.args['mac']
    nugget_obj = Nugget.objects(mac=mac).first()
    if nugget_obj == None:
        code = register_new_nugget(mac)
        return {
            'message-list': [
                "nugget.galletta.xyz/new/{}".format(code)
            ],
            'delay': 5
        }
    else:
        message_list = nugget_obj['message_list']
        lat = nugget_obj['weather_lat']
        lon = nugget_obj['weather_lon']
        cached_weather = nugget_obj['cached_weather']
        if nugget_obj['display_weather'] and ('report' not in cached_weather or (time.time() - cached_weather['time']) >= 180):
            cached_weather['time'] = time.time()
            cached_weather['report'] = weather(lat, lon)
        nugget_obj.save()    
        if nugget_obj['display_weather']:
            weather_data = cached_weather['report']
            current_temp = int(round(weather_data['current']['feels_like']))
            high = int(round(weather_data['daily'][0]['temp']['max']))
            low = int(round(weather_data['daily'][0]['temp']['min']))
            current_conditions = weather_data['daily'][0]['weather'][0]['main'] + " - " + weather_data['daily'][0]['weather'][0]['description']
            weather_string = pad(pad("Low:" + str(low) + " High:" + str(high), 16) + "Now Feels " + str(current_temp) + "°F", 32) + current_conditions
            message_list.insert(0,weather_string)
        return {
            'message-list': message_list,
            'delay': nugget_obj['delay']
        }


def register_new_nugget(mac):
    discovered = DiscoveredNugget.objects(mac=mac).first()
    if discovered == None:
        code = None
        while code is None or DiscoveredNugget.objects(code__exact=code).first() is not None:
            code = get_random_code(6)
        discovered = DiscoveredNugget(mac=mac, code=code)
        discovered.save()
    return discovered.code

def get_random_code(length):
    alphabet = string.ascii_uppercase + string.digits
    return ''.join((random.choice(alphabet) for i in range(length)))

@app.route('/new/<code>', methods=['GET', 'POST'])
def new(code):
    if request.method == 'GET':
        if not flask_login.current_user.is_authenticated:
            session['url'] = url_for('new', code=code)
            return redirect(url_for('login'))
        return render_template('new.html', code=code)
    else:
        discovered = DiscoveredNugget.objects(code__exact=code).first()
        if discovered == None:
            Flask.abort(401)
        else:
            new_nugget = Nugget()
            new_nugget.message_list = []
            new_nugget.name = request.form['name']
            new_nugget.mac = discovered['mac']
            new_nugget.assigner = request.form['assigner']
            new_nugget.assignee = flask_login.current_user.username
            new_nugget.weather_lat = "0"
            new_nugget.weather_lon = "0"
            new_nugget.display_weather = False
            new_nugget.delay = 5
            new_nugget.cached_weather = None
            new_nugget.save()
            return redirect(url_for('home'))
        


@app.route('/update/<nugget_id>', methods=['POST'])
def update(nugget_id):
    to_update = Nugget.objects(id=nugget_id).first()
    message_list = []
    data = request.form.listvalues()
    print(data)
    for message in request.form.values():
        if len(message) > 0:
            message_list.append(message)
    to_update.message_list = message_list
    to_update.save()
    flash('Updated Successfully')
    return(redirect(url_for('home')))

@app.route('/update-my/<nugget_id>', methods=['POST'])
def update_my(nugget_id):
    to_update = Nugget.objects(id=nugget_id).get()
    try:
        to_update['display_weather'] = (request.form['display_weather'] == 'on') 
    except KeyError:
        to_update['display_weather'] = False
    to_update['weather_lat'] = request.form['weather_lat']
    to_update['weather_lon'] = request.form['weather_lon']
    to_update['delay'] = request.form['delay']
    to_update.save()
    flash('Updated Successfully')
    return(redirect(url_for('home')))

def weather(lat, lon):
    params= {
        'lat': lat,
        'lon': lon,
        'exclude': 'minutely,hourly',
        'units': 'imperial',
        'appid': WEATHER_API_KEY
    }
    weather = requests.get('https://api.openweathermap.org/data/2.5/onecall', params=params)
    return weather.json()

def pad(s, n):
    s = str(s)
    if len(s) >= n:
        return s[:n]
    else:
        to_add = n - len(s)
        return s + str(" " * to_add)

if __name__ == '__main__':
   app.run()
