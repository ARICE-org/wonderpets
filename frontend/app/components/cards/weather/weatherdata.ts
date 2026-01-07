// forecastData.ts
const forecastData = {
  hourly: [
    { time: "Now", temp: 26, icon: require("../../../Images/Rain.png") },
    { time: "18:00", temp: 25, icon: require("../../../Images/cloud.png") },
    { time: "19:00", temp: 25, icon: require("../../../Images/cloud.png") },
    { time: "20:00", temp: 25, icon: require("../../../Images/cloud.png") },
    { time: "21:00", temp: 25, icon: require("../../../Images/sun.png") },
    { time: "22:00", temp: 24, icon: require("../../../Images/sun.png") },
    { time: "23:00", temp: 25, icon: require("../../../Images/cloud.png") },
  ],
  daily: [
    { day: "TODAY", temp: "26°C", wind: "12.2 km/h" },
    { day: "TUE", temp: "31°C", wind: "12.0 km/h" },
    { day: "WED", temp: "29°C", wind: "11.5 km/h" },
    { day: "THU", temp: "30°C", wind: "9.3 km/h" },
    { day: "FRI", temp: "31°C", wind: "12.0 km/h" },
    { day: "SAT", temp: "29°C", wind: "11.5 km/h" },
    { day: "SUN", temp: "30°C", wind: "9.3 km/h" },
  ],
};

export default forecastData;
