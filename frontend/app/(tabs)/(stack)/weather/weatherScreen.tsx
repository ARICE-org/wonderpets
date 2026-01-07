import { VStack, ScrollView, Box } from "@gluestack-ui/themed";

import LocationLabel from "../../../components/cards/weather/locationlabel";
import CurrentWeather from "../../../components/cards/weather/currentweather";
import HourlyForecast from "../../../components/cards/weather/hourlyforecast";
import WeatherForecast from "@/app/components/cards/weather/weatherforecast";
import forecastData from "../../../components/cards/weather/weatherdata";

export default function WeatherScreen() {
  return (
    <Box flex={1} bg="$white" py={16}>
      <ScrollView showsVerticalScrollIndicator={false}>
        <VStack px="$5" space="md">
          <LocationLabel city="Naga City" date="October 8, 2024" />

          <CurrentWeather
            temperature={26}
            condition="Rainy / Cloudy"
            icon={require("../../../Images/Rain.png")}
          />

          <HourlyForecast data={forecastData.hourly} />

          <WeatherForecast data={forecastData.daily} />
        </VStack>
      </ScrollView>
    </Box>
  );
}
