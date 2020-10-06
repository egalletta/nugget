from flask_login import UserMixin
from mongoengine import Document, StringField

class User(Document, UserMixin):
    username = StringField(required=True)
    password = StringField(required=True)
