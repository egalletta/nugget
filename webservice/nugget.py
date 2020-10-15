from mongoengine import Document, StringField, ListField, BooleanField, IntField, DictField

class Nugget(Document):
    target = StringField() # deprecated
    message_list = ListField(StringField())
    name = StringField()
    mac = StringField()
    assigner = StringField()
    assignee = StringField()
    weather_lat = StringField()
    weather_lon = StringField()
    display_weather = BooleanField()
    delay = IntField()
    cached_weather = DictField()

class DiscoveredNugget(Document):
    mac = StringField()
    code = StringField()