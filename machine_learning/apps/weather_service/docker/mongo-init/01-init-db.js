// MongoDB initialization script for FuXi-S2S
// Creates the arice database with required collections

// Switch to the arice database
db = db.getSiblingDB("arice");

// Create collections
db.createCollection("weather_member_forecasts");
db.createCollection("weather_final_forecasts");
db.createCollection("stations");
db.createCollection("runs");

// Create indexes for efficient queries
db.weather_member_forecasts.createIndex({ run_id: 1 });
db.weather_member_forecasts.createIndex({ "station.name": 1 });
db.weather_member_forecasts.createIndex({ valid_time: 1 });
db.weather_member_forecasts.createIndex({ init_time: 1, lead_time_days: 1 });

db.weather_final_forecasts.createIndex({ run_id: 1 });
db.weather_final_forecasts.createIndex({ "station.name": 1 });
db.weather_final_forecasts.createIndex({ valid_time: 1 });
db.weather_final_forecasts.createIndex({ init_time: 1 });

db.runs.createIndex({ run_id: 1 }, { unique: true });
db.runs.createIndex({ created_at: -1 });

db.stations.createIndex({ name: 1 }, { unique: true });

// Insert default stations
db.stations.insertMany([
  {
    name: "Pacol, Naga City",
    lat: 13.657096,
    lon: 123.224535,
    description: "CBSUA Weather Station",
  },
  {
    name: "Pili, Camarines Sur",
    lat: 13.58,
    lon: 123.28,
    description: "Pili Synoptic Station",
  },
  {
    name: "Naga City",
    lat: 13.62,
    lon: 123.19,
    description: "Naga City Center",
  },
]);

print("✅ MongoDB initialization complete for arice database");
