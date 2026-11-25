import os
from datetime import timedelta
from flask import Flask, jsonify, make_response, request, session
from flask_cors import CORS
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_jwt_identity,
    get_jwt,
    set_refresh_cookies,
    unset_jwt_cookies
)
from dotenv import load_dotenv
from pydantic import ValidationError
import requests
import datetime
import time
from flask_apscheduler import APScheduler

from extensions import db, jwt, bcrypt, migrate
from models import User, List, Weather, City, Forecast
from schemas import LoginSchema, RegisterSchema
from blocklist import BLOCKLIST

import traceback

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIES_SAMESITE"] = "Lax"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
jwt.init_app(app)

scheduler = APScheduler()
scheduler.init_app(app)

frontend_url = os.getenv("FRONTEND_URL")
CORS(
    app, 
    resources={r"/api/*": {"origins": frontend_url}},
    supports_credentials=True
)


@app.route("/api/register", methods=["POST"])
def register():
    raw_data = request.get_json(silent=True) or {}

    try:
        payload = RegisterSchema(**raw_data)
    except ValidationError as err:

        field_error_messages = {
            "firstName": "First name must have at least one character.",
            "lastName": "Last name must have at least one character.",
            "email": "Plese, enter a valid email address.",
            "password": "Pasword must have at least 6 characters"
        }

        def get_validation_message(validation_err):
            first_error = validation_err.errors()[0]
            field_name = first_error["loc"][0]
            return field_error_messages.get(field_name, first_error["msg"])
        
        return jsonify({"message": get_validation_message(err)}), 400

    email = payload.email.lower()

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "An account with this email already exists."}), 409

    hashed_password = bcrypt.generate_password_hash(payload.password).decode("utf-8")
    user = User(
        firstName=payload.firstName,
        lastName=payload.lastName,
        email=email,
        password_hash=hashed_password,
    )

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Registration success"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")
        return jsonify({"message": "An unexpected error occurred during sign up. Try again!"}), 500



@app.route("/api/login", methods = ["POST"])
def login():
    raw_data = request.get_json(silent=True) or {}

    try:
        payload = LoginSchema(**raw_data)
    except ValidationError:
        return jsonify({"message": "Invalid user credentials"}), 401
    
    email = payload.email.lower()
    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password_hash, payload.password):
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        response = jsonify({
            "message": "Login Success",
            "access_token": access_token,
            "user_info": {
                "id": user.id,
                "firstName": user.firstName,
                "is_admin": user.is_admin
            }
        })
        set_refresh_cookies(response, refresh_token)
        return response, 200
    
    return jsonify({"message": "Invalid user credentials"}), 401


@app.route("/api/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, int(current_user_id))
    if not user:
        return jsonify({"message": "User not found"})

    new_access_token = create_access_token(identity=current_user_id)
    return jsonify({
        "access_token": new_access_token,
        "user_info": {
            "id": user.id,
            "firstName": user.firstName,
            "is_admin": user.is_admin
        }
    }), 200


@app.route("/api/logout", methods=["POST"])
@jwt_required(verify_type=False, optional=True)
def logout():
    token = get_jwt()
    if token:
        BLOCKLIST.add(token["jti"])

    refresh_cookie = request.cookies.get("refresh_token_cookie")
    if refresh_cookie:
        try:
            decoded_refresh = decode_token(refresh_cookie)
            BLOCKLIST.add(decoded_refresh["jti"])
        except Exception:
            pass

    response = jsonify({"message": "Logged out successfully"})
    unset_jwt_cookies(response)
    return response, 200



@app.route("/api/weather", methods=["GET"])
@jwt_required()
def weather():
    try:
        current_user_id = int(get_jwt_identity())
        results = (
            db.session.query(User, List, Weather, City, Forecast)
            .join(List, User.id == List.user_id)
            .join(City, List.city_id == City.id)
            .join(Weather, Weather.city_id == City.id)
            .join(Forecast, Weather.city_id == Forecast.city_id)
            .filter(User.id == current_user_id)
            .all()
        )

        cards_data = []
        for r in results:
            cards_data.append({
                "user_name": r[0].firstName,
                "city_id": r[1].city_id,
                "city_name": r[2].city_name,
                "temp": r[2].temperature,
                "cond": r[2].condition,
                "humid": r[2].humidity,
                "w_speed": r[2].wind_speed,
                "w_icon": r[2].icon,
                "day1_t": r[4].day1_temp,
                "day2_t": r[4].day2_temp,
                "day3_t": r[4].day3_temp,
                "day4_t": r[4].day4_temp,
                "day5_t": r[4].day5_temp,
                "day1_i": r[4].day1_icon,
                "day2_i": r[4].day2_icon,
                "day3_i": r[4].day3_icon,
                "day4_i": r[4].day4_icon,
                "day5_i": r[4].day5_icon,
                "day1_dt": r[4].day1_dt,
                "day2_dt": r[4].day2_dt,
                "day3_dt": r[4].day3_dt,
                "day4_dt": r[4].day4_dt,
                "day5_dt": r[4].day5_dt
            })
            
        return jsonify(cards_data), 200

    except Exception as e:
        return jsonify({"message": "Failed to load weather data."}), 500    


@app.route("/api/search", methods=["GET"])
@jwt_required()
def search():
    try:
        current_user_id = int(get_jwt_identity())
        saved_cities = db.session.query(List.city_id, List.city_name).filter_by(user_id=current_user_id)
        all_cities = db.session.query(City.id, City.city_name)
        available_cities = all_cities.except_(saved_cities).all()

        dropdown_data = [
            {"id": city.id, "name": city.city_name}
            for city in available_cities
        ]
        return jsonify(dropdown_data), 200

    except Exception as e:
        return jsonify({"message": "Failed to load cities"}), 500


def fetch_and_save_city_weather(city_id, city_name):
    url_weather = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid={WEATHER_API_KEY}"

    weather_res = requests.get(url_weather, timeout=10)
    weather_res.raise_for_status()
    r = weather_res.json()

    weather_obj = {
        "city_id": city_id,
        "city": city_name,
        "temperature": r["main"]["temp"],
        "condition": r["weather"][0]["description"],
        "humidity":r["main"]["humidity"],
        "wind_speed":r["wind"]["speed"],
        "icon":r["weather"][0]["icon"]
    }

    weather_obj_db = Weather(
        city_id=weather_obj["city_id"],
        city_name=weather_obj["city"],
        temperature=weather_obj["temperature"],
        condition=weather_obj["condition"],
        humidity=weather_obj["humidity"],
        wind_speed=weather_obj["wind_speed"],
        icon=weather_obj["icon"],
    )

    url_forecast = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&units=metric&appid={WEATHER_API_KEY}"
    forecast_res = requests.get(url_forecast, timeout=10)
    forecast_res.raise_for_status()
    r_forecast = forecast_res.json()

    forecast_obj = {
        "city_id": city_id,
        "city": city_name,
        "day1_t": r_forecast["list"][7]["main"]["temp"],
        "day2_t": r_forecast["list"][15]["main"]["temp"],
        "day3_t": r_forecast["list"][23]["main"]["temp"],
        "day4_t": r_forecast["list"][31]["main"]["temp"],
        "day5_t": r_forecast["list"][39]["main"]["temp"],
        "day1_i": r_forecast["list"][7]["weather"][0]["icon"],
        "day2_i": r_forecast["list"][15]["weather"][0]["icon"],
        "day3_i": r_forecast["list"][23]["weather"][0]["icon"],
        "day4_i": r_forecast["list"][31]["weather"][0]["icon"],
        "day5_i": r_forecast["list"][39]["weather"][0]["icon"],
        "day1_date": r_forecast["list"][7]["dt"],
        "day2_date": r_forecast["list"][15]["dt"],
        "day3_date": r_forecast["list"][23]["dt"],
        "day4_date": r_forecast["list"][31]["dt"],
        "day5_date": r_forecast["list"][39]["dt"],
    }

    forecast_obj_db = Forecast(
        city_id=forecast_obj["city_id"],
        city_name=forecast_obj["city"],
        day1_temp=forecast_obj["day1_t"],
        day2_temp=forecast_obj["day2_t"],
        day3_temp=forecast_obj["day3_t"],
        day4_temp=forecast_obj["day4_t"],
        day5_temp=forecast_obj["day5_t"],
        day1_icon=forecast_obj["day1_i"],
        day2_icon=forecast_obj["day2_i"],
        day3_icon=forecast_obj["day3_i"],
        day4_icon=forecast_obj["day4_i"],
        day5_icon=forecast_obj["day5_i"],
        day1_dt=datetime.datetime.fromtimestamp(int(forecast_obj["day1_date"])).strftime("%a"),
        day2_dt=datetime.datetime.fromtimestamp(int(forecast_obj["day2_date"])).strftime("%a"),
        day3_dt=datetime.datetime.fromtimestamp(int(forecast_obj["day3_date"])).strftime("%a"),
        day4_dt=datetime.datetime.fromtimestamp(int(forecast_obj["day4_date"])).strftime("%a"),
        day5_dt=datetime.datetime.fromtimestamp(int(forecast_obj["day5_date"])).strftime("%a"),
    )

    db.session.add(weather_obj_db)
    db.session.add(forecast_obj_db)


@app.route("/api/add", methods=["POST"])
@jwt_required()
def add_city():

    current_user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    selected_city_name = data.get("itemName", "").strip()

    if not selected_city_name:
        return jsonify({"error": "City name is required"}), 400

    city_obj = City.query.filter_by(city_name=selected_city_name).first()
    if not city_obj:
        return jsonify({"error": "City not found"}), 404

    if List.query.filter_by(user_id=current_user_id, city_id=city_obj.id).first():
        return jsonify({"error": "City is already in your list"}), 409

    try:
        user_city = List(
            user_id=current_user_id,
            city_id=city_obj.id,
            city_name=city_obj.city_name,
        )
        db.session.add(user_city)

        weather_exists = Weather.query.filter_by(city_id=city_obj.id).first() is not None
        if not weather_exists:
            fetch_and_save_city_weather(city_obj.id, city_obj.city_name)

        db.session.commit()
        return jsonify({"message": f"{city_obj.city_name} added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        print(str(e))
        return jsonify({"error": "An unexpected error occured"})


@app.route("/api/<int:city_id>/delete", methods=["DELETE"])
@jwt_required()
def delete_city(city_id):
    current_user_id = int(get_jwt_identity())

    try:
        deleted_count = List.query.filter_by(
            user_id=current_user_id,
            city_id=city_id
        ).delete()

        if deleted_count == 0:
            return jsonify({"error": "City not found in your list"}), 404

        db.session.commit()
        return jsonify({"message": "City successfully deleted"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error deleting city: {e}")
        return jsonify({"error": "Failed to delete city"}), 500


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLOCKLIST


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "message": "Unauthorized.",
    }), 401


def update_weather():
    with app.app_context():
        cities = Weather.query.all()

        url=f"https://api.openweathermap.org/data/2.5/weather?q={{}}&units=metric&appid={WEATHER_API_KEY}"
        weather_data=[]

        for city in cities:
            try:
                response = requests.get(url.format(city.city_name),
                                 timeout=(10, 30))
                response.raise_for_status()
                r = response.json()

            except requests.exceptions.RequestException as e:
                print(f"Skipping {city.city_name} due to API timeout/error: {e}", flush=True)
                continue

            weather_obj = {
                'city_id': city.city_id,
                'city': city.city_name,
                'temperature': r['main']['temp'],
                'description': r['weather'][0]['description'],
                'humidity': r['main']['humidity'],
                'windSpeed': r['wind']['speed'],
                'icon': r['weather'][0]['icon']
            }

            weather_data.append(weather_obj)


            city_to_update = db.session.query(Weather).filter(Weather.city_id == weather_obj['city_id']).first()

            city_to_update.temperature=weather_obj['temperature']
            city_to_update.condition=weather_obj['description']
            city_to_update.humidity=weather_obj['humidity']
            city_to_update.wind_speed=weather_obj['windSpeed']
            city_to_update.icon=weather_obj['icon']

            try:
                db.session.commit()

            except Exception as e:
                db.session.rollback()
                print(e)

            time.sleep(1)

        print(weather_data)



def update_forecast():
    with app.app_context():
        cities = Forecast.query.all()

        url_forecast = f"https://api.openweathermap.org/data/2.5/forecast?q={{}}&units=metric&appid={WEATHER_API_KEY}"
        forecast_data = []

        for city in cities:
            try:
                response = requests.get(url_forecast.format(city.city_name), timeout=(10, 30))
                response.raise_for_status()
                r_forecast = response.json()

            except requests.exceptions.RequestException as e:
                print(f"Skipping {city.city_name} due to API timeout/error: {e}", flush=True)
                continue

            forecast_obj = {
                'city_id': city.city_id,
                'city': city.city_name,
                'day1_t': r_forecast['list'][7]['main']['temp'],
                'day2_t': r_forecast['list'][15]['main']['temp'],
                'day3_t': r_forecast['list'][23]['main']['temp'],
                'day4_t': r_forecast['list'][31]['main']['temp'],
                'day5_t': r_forecast['list'][39]['main']['temp'],
                'day1_i': r_forecast['list'][7]['weather'][0]['icon'],
                'day2_i': r_forecast['list'][15]['weather'][0]['icon'],
                'day3_i': r_forecast['list'][23]['weather'][0]['icon'],
                'day4_i': r_forecast['list'][31]['weather'][0]['icon'],
                'day5_i': r_forecast['list'][39]['weather'][0]['icon'],
                'day1_date': r_forecast['list'][7]['dt'],
                'day2_date': r_forecast['list'][15]['dt'],
                'day3_date': r_forecast['list'][23]['dt'],
                'day4_date': r_forecast['list'][31]['dt'],
                'day5_date': r_forecast['list'][39]['dt']
            }

            forecast_data.append(forecast_obj)

            forecast_to_update = db.session.query(Forecast).filter(Forecast.city_id == forecast_obj['city_id']).first()

            forecast_to_update.day1_temp=forecast_obj['day1_t']
            forecast_to_update.day2_temp=forecast_obj['day2_t']
            forecast_to_update.day3_temp=forecast_obj['day3_t']
            forecast_to_update.day4_temp=forecast_obj['day4_t']
            forecast_to_update.day5_temp=forecast_obj['day5_t']
            forecast_to_update.day1_icon=forecast_obj['day1_i']
            forecast_to_update.day2_icon=forecast_obj['day2_i']
            forecast_to_update.day3_icon=forecast_obj['day3_i']
            forecast_to_update.day4_icon=forecast_obj['day4_i']
            forecast_to_update.day5_icon=forecast_obj['day5_i']
            forecast_to_update.day1_dt=datetime.datetime.fromtimestamp(int(forecast_obj['day1_date'])).strftime('%a')
            forecast_to_update.day2_dt=datetime.datetime.fromtimestamp(int(forecast_obj['day2_date'])).strftime('%a')
            forecast_to_update.day3_dt=datetime.datetime.fromtimestamp(int(forecast_obj['day3_date'])).strftime('%a')
            forecast_to_update.day4_dt=datetime.datetime.fromtimestamp(int(forecast_obj['day4_date'])).strftime('%a')
            forecast_to_update.day5_dt=datetime.datetime.fromtimestamp(int(forecast_obj['day5_date'])).strftime('%a')

            try:
                db.session.commit()

            except Exception as e:
                return str(e)

            time.sleep(1)

        print(forecast_data)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        scheduler.add_job(id='weather', func=update_weather, trigger="cron", hour=17, minute=9)
        scheduler.add_job(id='forecast', func=update_forecast, trigger="cron", hour=17, minute=11)
        scheduler.start()
        print("Scheduler running:", scheduler.running)
        app.run(port=5001, debug=False)


