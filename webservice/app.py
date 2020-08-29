from flask import Flask, request
from flask_pymongo import PyMongo
import os

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get('MONGOSTR')
mongo = PyMongo(app)

@app.route('/motd', methods=['GET'])
def hello_world():
    filt = {'target' : 'node-nora'}
    motd = mongo.db.messages.find_one(filt)
    return motd['motd']
    

@app.route('/update', methods=['PUT'])
def update():
    new_message = request.get_json()
    filt = {'target' : 'node-nora'}
    to_write = {"$set": {"motd": new_message['motd']}}
    mongo.db.messages.update_one(filt, to_write)
    result = {'result' : 'Updated successfully'}
    return result

if __name__ == '__main__':
   app.run()