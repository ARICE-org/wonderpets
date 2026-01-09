import { VStack, ScrollView, Box } from "@gluestack-ui/themed";
import { SafeAreaView } from "react-native-safe-area-context";

import LocationLabel from "../../../components/cards/weather/locationlabel";
import CurrentWeather from "../../../components/cards/weather/currentweather";
// import HourlyForecast from "../../../components/cards/weather/hourlyforecast";
import WeatherForecast from "@/app/components/cards/weather/weatherforecast";
import forecastData from "../../../Data/weatherdata";

export default function WeatherScreen() {
  return (
    // ✅ only TOP safe area
    <SafeAreaView style={{ flex: 1 }} edges={["top"]}>
      <Box flex={1} bg="$white">
        <ScrollView
          showsVerticalScrollIndicator={false}
          contentContainerStyle={{
            paddingTop: 16,
            paddingBottom: 8, // 👈 minimal bottom padding
          }}
        >
          <VStack mb="$5" space="md">
            <LocationLabel city="Naga City" date="October 8, 2024" />

            <CurrentWeather
              temperature={26}
              condition="Rainy / Cloudy"
              icon={require("../../../Images/Rain.png")}
            />

            {/* <HourlyForecast data={forecastData.hourly} /> */}

            <WeatherForecast data={forecastData.daily} />
          </VStack>
        </ScrollView>
      </Box>
    </SafeAreaView>
  );
}
