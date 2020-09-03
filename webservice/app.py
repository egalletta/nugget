from flask import Flask, request
from flask_pymongo import PyMongo
import os
import requests
import time

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get('MONGOSTR')
mongo = PyMongo(app)
WEATHER_API_KEY = os.environ.get('WEATHER_KEY')

cached_weather = {
    'time': None,
    'report': None
}

@app.route('/motd', methods=['GET'])
def motd():
    filt = {'target' : 'node-nora'}
    motd = mongo.db.messages.find_one(filt)
    message_list = motd['message-list']

    if cached_weather['report'] is None or (time.time() - cached_weather['time']) >= 180:
        cached_weather['time'] = time.time()
        cached_weather['report'] = weather()
        
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

def weather():
    params= {
        'lat': 42.361145,
        'lon': -71.057083,
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

@app.route('/update', methods=['PUT'])
def update():
    req_data = request.get_json()
    filt = {'target' : 'node-nora'}
    to_write = {"$set": {"message-list": req_data['message-list']}}
    mongo.db.messages.update_one(filt, to_write)
    result = {'result' : 'Updated successfully'}
    return result

if __name__ == '__main__':
   app.run()