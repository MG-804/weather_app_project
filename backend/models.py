from extensions import db, bcrypt


class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer(), db.ForeignKey('city.id'))
    city_name = db.Column(db.String(50), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)
    icon = db.Column(db.String(50))


class Forecast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer(), db.ForeignKey('city.id'))
    city_name = db.Column(db.String(50), nullable=False)
    day1_temp = db.Column(db.Float)
    day2_temp = db.Column(db.Float)
    day3_temp = db.Column(db.Float)
    day4_temp = db.Column(db.Float)
    day5_temp = db.Column(db.Float)
    day1_icon = db.Column(db.String(50))
    day2_icon = db.Column(db.String(50))
    day3_icon = db.Column(db.String(50))
    day4_icon = db.Column(db.String(50))
    day5_icon = db.Column(db.String(50))
    day1_dt = db.Column(db.Integer())
    day2_dt = db.Column(db.Integer())
    day3_dt = db.Column(db.Integer())
    day4_dt = db.Column(db.Integer())
    day5_dt = db.Column(db.Integer())


class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    city_id = db.Column(db.Integer(), db.ForeignKey('city.id'))
    city_name = db.Column(db.String(50))

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(50), nullable=False)
    weather = db.relationship(Weather, backref='city')
    forecast = db.relationship(Forecast, backref='city')
    city_list = db.relationship(List, backref='city')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    city_list = db.relationship(List, backref='user')