from flask import Flask
app = Flask(__name__)

@app.route('/motd', methods=['GET'])
def hello_world():
   return "Hello World (from the cloud!)!"

if __name__ == '__main__':
   app.run()