from mongoengine import Document, StringField, ListField, BooleanField, IntField

class Nugget(Document):
    target = StringField(required=True)
    message_list = ListField(StringField())
    name = StringField()
    mac = StringField()
    assigner = StringField()
    assignee = StringField()
    weather_lat = StringField()
    weather_lon = StringField()
    display_weather = BooleanField()
    delay = IntField()