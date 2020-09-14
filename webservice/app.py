from flask import Flask, request, flash, url_for, render_template, redirect
from flask_mongoengine import MongoEngine
import os
import requests
import time
import flask_login
import bcrypt

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

cached_weather = {
    'time': None,
    'report': None
}

class Nugget(db.Document):
    target = db.StringField(required=True)
    message_list = db.ListField(db.StringField())
    name = db.StringField()
    mac = db.StringField()
    assigner = db.StringField()
    assignee = db.StringField()
    weather_lat = db.StringField()
    weather_lon = db.StringField()

class User(db.Document, flask_login.UserMixin):
    username = db.StringField(required=True)
    password = db.StringField(required=True)

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
    nugget_obj = Nugget.objects(mac=mac).first_or_404()
    message_list = nugget_obj['message_list']
    lat = nugget_obj['weather_lat']
    lon = nugget_obj['weather_lon']

    if cached_weather['report'] is None or (time.time() - cached_weather['time']) >= 180:
        cached_weather['time'] = time.time()
        cached_weather['report'] = weather(lat, lon)
        
    weather_data = cached_weather['report']
    current_temp = int(round(weather_data['current']['feels_like']))
    high = int(round(weather_data['daily'][0]['temp']['max']))
    low = int(round(weather_data['daily'][0]['temp']['min']))
    current_conditions = weather_data['daily'][0]['weather'][0]['main'] + " - " + weather_data['daily'][0]['weather'][0]['description']
    weather_string = pad(pad("Low:" + str(low) + " High:" + str(high), 16) + "Now Feels " + str(current_temp) + "°F", 32) + current_conditions
    message_list.insert(0,weather_string)
    return {
        'message-list': message_list
    }

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

@app.route('/update/<nugget_id>', methods=['POST'])
def update(nugget_id):
    to_update = Nugget.objects(id=nugget_id).get_or_404()
    message_list = []
    data = request.form.listvalues()
    print(data)
    for message in request.form.values():
        message_list.append(message)
    to_update.message_list = message_list
    to_update.save()
    flash('Updated Successfully')
    return(redirect(url_for('home')))

if __name__ == '__main__':
   app.run()