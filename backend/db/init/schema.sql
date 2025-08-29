-- ========== ARICE FARMING DATABASE SCHEMA ==========
-- Create tables from UML Diagram

-- Farmer
CREATE TABLE farmer (
    farmer_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    location VARCHAR(100) NOT NULL
);

-- Farming History
CREATE TABLE farming_history (
    history_id VARCHAR(20) PRIMARY KEY,
    farmer_id VARCHAR(20) NOT NULL,
    history_date DATE,
    history_title VARCHAR(100),
    yields NUMERIC,
    FOREIGN KEY (farmer_id) REFERENCES farmer(farmer_id)
);

-- Season
CREATE TABLE season (
    season_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- Rice Variety
CREATE TABLE rice_variety (
    rice_variety_id VARCHAR(20) PRIMARY KEY,
    season_id VARCHAR(20) NOT NULL,
    rice_name VARCHAR(100) NOT NULL,
    growth_duration INT NOT NULL,
    color VARCHAR(20) NOT NULL,
    FOREIGN KEY (season_id) REFERENCES season(season_id)
);

-- Weather Data
CREATE TABLE weather_data (
    weather_id VARCHAR(20) PRIMARY KEY,
    datetime TIMESTAMP NOT NULL,
    max_temp DOUBLE PRECISION NOT NULL,
    min_temp DOUBLE PRECISION NOT NULL,
    rainfall DOUBLE PRECISION NOT NULL,
    humidity DOUBLE PRECISION NOT NULL,
    wind_speed DOUBLE PRECISION NOT NULL,
    wind_direct CHAR(1) NOT NULL
);

-- Variety Suggestion
CREATE TABLE variety_suggestion (
    variety_sugg_id VARCHAR(20) PRIMARY KEY,
    rice_variety_id VARCHAR(20) NOT NULL,
    date_generated TIMESTAMP NOT NULL,
    feedback BOOLEAN NOT NULL,
    FOREIGN KEY (rice_variety_id) REFERENCES rice_variety(rice_variety_id)
);

-- Farm Dataset
CREATE TABLE farm_dataset (
    farm_dataset_id VARCHAR(20) PRIMARY KEY,
    rice_variety_id VARCHAR(20) NOT NULL,
    weather_id VARCHAR(20) NOT NULL,
    analysis_id VARCHAR(20),
    planting_date_start TIMESTAMP NOT NULL,
    FOREIGN KEY (rice_variety_id) REFERENCES rice_variety(rice_variety_id),
    FOREIGN KEY (weather_id) REFERENCES weather_data(weather_id)
);

-- Farming Schedule
CREATE TABLE farming_schedule (
    schedule_id VARCHAR(20) PRIMARY KEY,
    farmer_id VARCHAR(20) NOT NULL,
    farm_dataset_id VARCHAR(20) NOT NULL,
    farmer_feedback BOOLEAN NOT NULL,
    FOREIGN KEY (farmer_id) REFERENCES farmer(farmer_id),
    FOREIGN KEY (farm_dataset_id) REFERENCES farm_dataset(farm_dataset_id)
);

-- Task
CREATE TABLE task (
    task_id VARCHAR(20) PRIMARY KEY,
    schedule_id VARCHAR(20) NOT NULL,
    title VARCHAR(50) NOT NULL,
    caption VARCHAR(200) NOT NULL,
    status BOOLEAN NOT NULL,
    priority_level CHAR(1) NOT NULL,
    feedback BOOLEAN NOT NULL,
    date TIMESTAMP NOT NULL,
    FOREIGN KEY (schedule_id) REFERENCES farming_schedule(schedule_id)
);

-- Soil Sensor Device
CREATE TABLE soil_sensor_device (
    sensor_id INT PRIMARY KEY,
    sensor_desc VARCHAR(50) NOT NULL,
    curr_date DATE NOT NULL,
    curr_time TIME NOT NULL,
    device_status BOOLEAN NOT NULL
);

-- Soil Data
CREATE TABLE soil_data (
    soil_id VARCHAR(20) PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    soil_moisture DOUBLE PRECISION NOT NULL,
    soil_ph DOUBLE PRECISION NOT NULL,
    nitrogen_level DOUBLE PRECISION NOT NULL,
    phosphorus_level DOUBLE PRECISION NOT NULL,
    potassium_level DOUBLE PRECISION NOT NULL,
    sensor_id INT NOT NULL,
    FOREIGN KEY (sensor_id) REFERENCES soil_sensor_device(sensor_id)
);

-- Soil Analysis
CREATE TABLE soil_analysis (
    analysis_id VARCHAR(20) PRIMARY KEY,
    soil_id VARCHAR(20) NOT NULL,
    analysis_date TIMESTAMP NOT NULL,
    soil_health_summary TEXT NOT NULL,
    recommendations TEXT NOT NULL,
    FOREIGN KEY (soil_id) REFERENCES soil_data(soil_id)
);
