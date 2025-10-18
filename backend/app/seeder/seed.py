from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import *
import random

from app.utils.auth.password_hashing import hash_password

from faker import Faker
fake = Faker("tl_PH")

def seed_users(session: Session, n=10):
    hasData = session.query(User).first()
    if hasData:
        print("Users already seeded, skipping...")
        return
    try:
        for _ in range(n):
            gen_uuid = fake.uuid4()

            user = User(
                user_id=gen_uuid,
                email=fake.email(),
                password=hash_password(fake.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)),
                phone_number=fake.mobile_number()
            )
            session.add(user)
            session.commit()

            farmer = Farmer(
                farmer_id=gen_uuid,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                address="Pacol, Naga City",
            )

            session.add(farmer)
            session.commit()

        print("Seeding Users/Farmers")
    except Exception as e:
        session.rollback()
        print(f"Error seeding users/farmers: {e}")

def seed_seasons(session: Session, n=4):
    hasData = session.query(Season).first()
    if hasData:
        print("Seasons already seeded, skipping...")
        return
    try:
        for _ in range(n):
            season = Season(
                season_id=fake.uuid4(),
                name=fake.word().capitalize()
            )
            session.merge(season)
        session.commit()
        print("Seeding Seasons")
    except Exception as e:
        session.rollback()
        print(f"Error seeding seasons: {e}")

def seed_rice_varieties(session: Session, n=10):
    hasData = session.query(RiceVariety).first()
    if hasData:
        print("Rice Varieties already seeded, skipping...")
        return

    try:
        season_ids = [s.season_id for s in session.query(Season).all()]
        for _ in range(n):
            rice = RiceVariety(
                rice_variety_id=fake.uuid4(),
                season_id=random.choice(season_ids),
                rice_name=fake.word().capitalize(),
                growth_duration=random.randint(90, 150),
                color=random.choice(["white", "brown", "red", "black"])
            )
            session.merge(rice)
        session.commit()
        print("Seeding Rice Varieties")
    except Exception as e:
        session.rollback()
        print(f"Error seeding rice varieties: {e}")

def seed_weather_data(session: Session, n=10):
    hasData = session.query(WeatherData).first()
    if hasData:
        print("Weather Data already seeded, skipping...")
        return

    try:
        for _ in range(n):
            weather = WeatherData(
                weather_id=fake.uuid4(),
                date=fake.date_time_this_year(),
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
    except Exception as e:
        session.rollback()
        print(f"Error seeding weather data: {e}")

def seed_farming_history(session: Session, n=10):
    hasData = session.query(FarmingHistory).first()
    if hasData:
        print("Farming History already seeded, skipping...")
        return

    try:
        farmer_ids = [f.farmer_id for f in session.query(Farmer).all()]
        for _ in range(n):
            history = FarmingHistory(
                history_id=fake.uuid4(),
                farmer_id=random.choice(farmer_ids),
                history_date=fake.date_this_decade(before_today=True),
                history_title=fake.sentence(nb_words=4),
                yields=round(random.uniform(1, 10), 2)
            )
            session.merge(history)
        session.commit()
        print("Seeding Farming History")
    except Exception as e:
        session.rollback()
        print(f"Error seeding farming history: {e}")

def seed_variety_suggestion(session: Session, n=10):
    hasData = session.query(VarietySuggestion).first()
    if hasData:
        print("Variety Suggestion already seeded, skipping...")
        return

    try:
        rice_ids = [r.rice_variety_id for r in session.query(RiceVariety).all()]
        for _ in range(n):
            suggestion = VarietySuggestion(
                variety_sugg_id=fake.uuid4(),
                rice_variety_id=random.choice(rice_ids),
                feedback=random.choice([True, False]),
                created_date=fake.date_time_this_year(),
            )
            session.merge(suggestion)
        session.commit()
        print("Seeding Variety Suggestion")
    except Exception as e:
        session.rollback()
        print(f"Error seeding variety suggestion: {e}")

def seed_soil_sensor_device(session: Session, n=5):
    hasData = session.query(SoilSensorDevice).first()
    if hasData:
        print("Soil Sensor Device already seeded, skipping...")
        return

    try:
        for _ in range(n):
            sensor = SoilSensorDevice(
                sensor_id=fake.uuid4(),
                sensor_desc=fake.word().capitalize(),
                created_date=fake.date_time_this_year(),
                device_status=random.choice([True, False])
            )
            session.merge(sensor)
        session.commit()
        print("Seeding Soil Sensor Device")
    except Exception as e:
        session.rollback()
        print(f"Error seeding soil sensor device: {e}")

def seed_soil_data(session: Session, n=10):
    hasData = session.query(SoilData).first()
    if hasData:
        print("Soil Data already seeded, skipping...")
        return

    try:
        sensor_ids = [s.sensor_id for s in session.query(SoilSensorDevice).all()]
        for _ in range(n):
            soil = SoilData(
                soil_id=fake.uuid4(),
                datetimestamp=fake.date_time_this_year(),
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
    except Exception as e:
        session.rollback()
        print(f"Error seeding soil data: {e}")

def seed_soil_analysis(session: Session, n=10):
    hasData = session.query(SoilAnalysis).first()
    if hasData:
        print("Soil Analysis already seeded, skipping...")
        return

    try:
        soil_ids = [s.soil_id for s in session.query(SoilData).all()]
        for _ in range(n):
            analysis = SoilAnalysis(
                analysis_id=fake.uuid4(),
                soil_id=random.choice(soil_ids),
                analysis_date=fake.date_time_this_year(),
                soil_health_summary=fake.sentence(),
                recommendations=fake.sentence()
            )
            session.merge(analysis)
        session.commit()
        print("Seeding Soil Analysis")
    except Exception as e:
        session.rollback()
        print(f"Error seeding soil analysis: {e}")

def seed_farm_dataset(session: Session, n=10):
    hasData = session.query(FarmDataset).first()
    if hasData:
        print("Farm Dataset already seeded, skipping...")
        return

    try:
        rice_ids = [r.rice_variety_id for r in session.query(RiceVariety).all()]
        weather_ids = [w.weather_id for w in session.query(WeatherData).all()]
        analysis_ids = [a.analysis_id for a in session.query(SoilAnalysis).all()]
        for _ in range(n):
            farm = FarmDataset(
                farm_dataset_id=fake.uuid4(),
                rice_variety_id=random.choice(rice_ids),
                weather_id=random.choice(weather_ids),
                analysis_id=random.choice(analysis_ids),
                planting_date_start=fake.date_time_this_year()
            )
            session.merge(farm)
        session.commit()
        print("Seeding Farm Dataset")
    except Exception as e:
        session.rollback()
        print(f"Error seeding farm dataset: {e}")

def seed_farming_schedule(session: Session, n=10):
    hasData = session.query(FarmingSchedule).first()
    if hasData:
        print("Farming Schedule already seeded, skipping...")
        return

    try:
        farmer_ids = [f.farmer_id for f in session.query(Farmer).all()]
        farm_ids = [f.farm_dataset_id for f in session.query(FarmDataset).all()]
        for _ in range(n):
            schedule = FarmingSchedule(
                schedule_id=fake.uuid4(),
                farmer_id=random.choice(farmer_ids),
                farm_dataset_id=random.choice(farm_ids),
                farmer_feedback=random.choice([True, False])
            )
            session.merge(schedule)
        session.commit()
        print("Seeding Farming Schedule")
    except Exception as e:
        session.rollback()
        print(f"Error seeding farming schedule: {e}")

def seed_task(session: Session, n=10):
    hasData = session.query(Task).first()
    if hasData:
        print("Task already seeded, skipping...")
        return

    try:
        schedule_ids = [s.schedule_id for s in session.query(FarmingSchedule).all()]
        for _ in range(n):
            task = Task(
                task_id=fake.uuid4(),
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
    except Exception as e:
        session.rollback()
        print(f"Error seeding task: {e}")

def run_all_seeders():
    session = SessionLocal()
    try:
        seed_users(session)
        seed_seasons(session)
        seed_rice_varieties(session)
        seed_weather_data(session)
        seed_farming_history(session)
        seed_variety_suggestion(session)
        seed_soil_sensor_device(session)
        seed_soil_data(session)
        seed_soil_analysis(session)
        seed_farm_dataset(session)
        seed_farming_schedule(session)
        seed_task(session)
        session.close()
    except Exception as e:
        session.rollback()
        print(f"Error running seeders: {e}")

if __name__ == "__main__":
    run_all_seeders()
