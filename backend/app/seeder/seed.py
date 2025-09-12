import uuid

from sqlalchemy.orm import Session
from app.db import SessionLocal, engine
from app.models import *
from faker import Faker
import random

fake = Faker()

def seed_users(session: Session, n=10):
    for _ in range(n):
        gen_uuid = uuid.uuid4()

        user = User(
            uuid=gen_uuid,
            email=fake.email(),
            hashed_password=fake.password(length=16, special_chars=True, digits=False, upper_case=True, lower_case=False),
        )
        session.add(user)
        session.commit()

        farmer = Farmer(
            farmer_id=gen_uuid,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            address="Pacol, Naga City",
            phone_number=fake.phone_number()
        )

        session.add(farmer)
        session.commit()

    print("Seeding Users/Farmers")

def seed_seasons(session: Session, n=4):
    for i in range(n):
        season = Season(
            season_id=f"season{i+1}",
            name=fake.word().capitalize()
        )
        session.merge(season)
    session.commit()
    print("Seeding Seasons")

def seed_rice_varieties(session: Session, n=10):
    season_ids = [s.season_id for s in session.query(Season).all()]
    for _ in range(n):
        rice = RiceVariety(
            rice_variety_id=fake.uuid4()[:20],
            season_id=random.choice(season_ids),
            rice_name=fake.word().capitalize(),
            growth_duration=random.randint(90, 150),
            color=random.choice(["white", "brown", "red", "black"])
        )
        session.merge(rice)
    session.commit()
    print("Seeding Rice Varieties")

def seed_weather_data(session: Session, n=10):
    for _ in range(n):
        weather = WeatherData(
            weather_id=fake.uuid4()[:20],
            datetime=fake.date_time_this_year(),
            max_temp=round(random.uniform(30, 40), 2),
            min_temp=round(random.uniform(20, 29), 2),
            rainfall=round(random.uniform(0, 100), 2),
            humidity=round(random.uniform(50, 100), 2),
            wind_speed=round(random.uniform(0, 20), 2),
            wind_direct=random.choice(["N", "S", "E", "W"])
        )
        session.merge(weather)
    session.commit()
    print("Seeding Weather Data")

def seed_farm_dataset(session: Session, n=10):
    rice_ids = [r.rice_variety_id for r in session.query(RiceVariety).all()]
    weather_ids = [w.weather_id for w in session.query(WeatherData).all()]
    for _ in range(n):
        farm = FarmDataset(
            farm_dataset_id=fake.uuid4()[:20],
            rice_variety_id=random.choice(rice_ids),
            weather_id=random.choice(weather_ids),
            analysis_id=None,
            planting_date_start=fake.date_time_this_year()
        )
        session.merge(farm)
    session.commit()
    print("Seeding Farm Dataset")

def seed_farming_history(session: Session, n=10):
    farmer_ids = [f.farmer_id for f in session.query(Farmer).all()]
    for _ in range(n):
        history = FarmingHistory(
            history_id=fake.uuid4()[:20],
            farmer_id=random.choice(farmer_ids),
            history_date=fake.date_this_decade(),
            history_title=fake.sentence(nb_words=4),
            yields=round(random.uniform(1, 10), 2)
        )
        session.merge(history)
    session.commit()
    print("Seeding Farming History")

def seed_variety_suggestion(session: Session, n=10):
    rice_ids = [r.rice_variety_id for r in session.query(RiceVariety).all()]
    for _ in range(n):
        suggestion = VarietySuggestion(
            variety_sugg_id=fake.uuid4()[:20],
            rice_variety_id=random.choice(rice_ids),
            date_generated=fake.date_time_this_year(),
            feedback=random.choice([True, False])
        )
        session.merge(suggestion)
    session.commit()
    print("Seeding Variety Suggestion")

def seed_farming_schedule(session: Session, n=10):
    farmer_ids = [f.farmer_id for f in session.query(Farmer).all()]
    farm_ids = [f.farm_dataset_id for f in session.query(FarmDataset).all()]
    for _ in range(n):
        schedule = FarmingSchedule(
            schedule_id=fake.uuid4()[:20],
            farmer_id=random.choice(farmer_ids),
            farm_dataset_id=random.choice(farm_ids),
            farmer_feedback=random.choice([True, False])
        )
        session.merge(schedule)
    session.commit()
    print("Seeding Farming Schedule")

def seed_task(session: Session, n=10):
    schedule_ids = [s.schedule_id for s in session.query(FarmingSchedule).all()]
    for _ in range(n):
        task = Task(
            task_id=fake.uuid4()[:20],
            schedule_id=random.choice(schedule_ids),
            title=fake.word().capitalize(),
            caption=fake.sentence(),
            status=random.choice([True, False]),
            priority_level=random.choice(["A", "B", "C"]),
            feedback=random.choice([True, False]),
            date=fake.date_time_this_year()
        )
        session.merge(task)
    session.commit()
    print("Seeding Task")

def seed_soil_sensor_device(session: Session, n=5):
    for i in range(n):
        sensor = SoilSensorDevice(
            sensor_id=i+1,
            sensor_desc=fake.word().capitalize(),
            curr_date=fake.date_this_year(),
            curr_time=fake.time_object(),
            device_status=random.choice([True, False])
        )
        session.merge(sensor)
    session.commit()
    print("Seeding Soil Sensor Device")

def seed_soil_data(session: Session, n=10):
    sensor_ids = [s.sensor_id for s in session.query(SoilSensorDevice).all()]
    for _ in range(n):
        soil = SoilData(
            soil_id=fake.uuid4()[:20],
            timestamp=fake.date_time_this_year(),
            soil_moisture=round(random.uniform(10, 50), 2),
            soil_ph=round(random.uniform(5, 8), 2),
            nitrogen_level=round(random.uniform(0, 100), 2),
            phosphorus_level=round(random.uniform(0, 100), 2),
            potassium_level=round(random.uniform(0, 100), 2),
            sensor_id=random.choice(sensor_ids)
        )
        session.merge(soil)
    session.commit()
    print("Seeding Soil Data")

def seed_soil_analysis(session: Session, n=10):
    soil_ids = [s.soil_id for s in session.query(SoilData).all()]
    for _ in range(n):
        analysis = SoilAnalysis(
            analysis_id=fake.uuid4()[:20],
            soil_id=random.choice(soil_ids),
            analysis_date=fake.date_time_this_year(),
            soil_health_summary=fake.sentence(),
            recommendations=fake.sentence()
        )
        session.merge(analysis)
    session.commit()
    print("Seeding Soil Analysis")

def run_all_seeders():
    session = SessionLocal()
    seed_users(session)
    seed_seasons(session)
    seed_rice_varieties(session)
    seed_weather_data(session)
    seed_farm_dataset(session)
    seed_farming_history(session)
    seed_variety_suggestion(session)
    seed_farming_schedule(session)
    seed_task(session)
    seed_soil_sensor_device(session)
    seed_soil_data(session)
    seed_soil_analysis(session)
    session.close()

if __name__ == "__main__":
    run_all_seeders()
