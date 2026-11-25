from app import app
from extensions import db
from models import City

INITIAL_CITIES = [
    "Moscow", "London", "New York", "Tokyo", "Paris",
    "Berlin", "Madrid", "Rome", "Toronto", "Sydney",
    "Dubai", "Singapore", "Seoul", "Istanbul", "Bangkok",
    "Amsterdam", "Vienna", "Prague", "Warsaw", "Stockholm",
    "Oslo", "Lisbon", "Athens", "Cairo", "Mumbai",
    "Beijing", "Los Angeles", "Chicago", "Rio de Janeiro", "Buenos Aires",
]


def seed_cities():
    with app.app_context():
        existing_cities = set()
        for city in City.query.all():
            existing_cities.add(city.city_name)

        new_cities = []
        for name in INITIAL_CITIES:
            if name not in existing_cities:
                new_cities.append(City(city_name=name))

        if new_cities:
            db.session.bulk_save_objects(new_cities)
            db.session.commit()

        print(f"Seeding complete! Added {len(new_cities)} new cities.")


if __name__ == "__main__":
    seed_cities()
