import { useState, useEffect, useCallback, useRef } from "react";
import {
  VStack,
  HStack,
  ScrollView,
  Box,
  Text,
  Spinner,
  Pressable,
} from "@gluestack-ui/themed";
import { SafeAreaView } from "react-native-safe-area-context";
import {
  RefreshControl,
  Animated,
  Easing,
  StyleSheet,
  Image,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { router, useSegments } from "expo-router";

// Backend API configuration
const API_BASE_URL = "http://10.0.2.2:8000"; // Use 10.0.2.2 for Android emulator, localhost for iOS

// Theme colors
const THEME = {
  primary: "#1DB954",
  primaryLight: "#E8F8EE",
  background: "#F5F7FA",
  text: "#1A1A1A",
  textLight: "#666666",
  card: "#FFFFFF",
};

// 3D Weather Icons
const WEATHER_ICONS = {
  rainy: require("../../../Images/Rain.png"),
  showers: require("../../../Images/Rain.png"),
  cloudy: require("../../../Images/cloud.png"),
  cool: require("../../../Images/cloud.png"),
  clear: require("../../../Images/sun.png"),
};

interface WeatherForecast {
  datetime: string;
  weekdate: string;
  rainfall_mm: string;
  temperature_c: string;
  dewpoint_c: string;
  pressure_pa: string;
  wind_u10: string;
  wind_v10: string;
  wind_speed_ms: string;
  wind_speed_kmh: string;
  wind_direction_deg: string;
  wind_direction: string;
  weather: string;
}

// Get 3D weather icon
const getWeather3DIcon = (weather: string) => {
  switch (weather.toLowerCase()) {
    case "rainy":
      return WEATHER_ICONS.rainy;
    case "showers":
      return WEATHER_ICONS.showers;
    case "cloudy":
      return WEATHER_ICONS.cloudy;
    case "cool":
      return WEATHER_ICONS.cool;
    case "clear":
    default:
      return WEATHER_ICONS.clear;
  }
};

const getWeather2DIcon = (weather: string) => {
  switch (weather.toLowerCase()) {
    case "rainy":
      return { name: "rainy" as const, color: "#6BB3D9" };
    case "showers":
      return { name: "rainy-outline" as const, color: "#6BB3D9" };
    case "cloudy":
      return { name: "cloudy" as const, color: "#9AA4B2" };
    case "cool":
      return { name: "snow" as const, color: "#9AA4B2" };
    case "clear":
    default:
      return { name: "sunny" as const, color: "#FFB020" };
  }
};

// Custom hook for fade-in animation
const useFadeIn = (delay: number = 0) => {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(30)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 600,
        delay,
        useNativeDriver: true,
        easing: Easing.out(Easing.cubic),
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 600,
        delay,
        useNativeDriver: true,
        easing: Easing.out(Easing.cubic),
      }),
    ]).start();
  }, []);

  return { fadeAnim, slideAnim };
};

// Bouncing icon animation
const useBouncingIcon = () => {
  const bounceAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const bounce = Animated.loop(
      Animated.sequence([
        Animated.timing(bounceAnim, {
          toValue: -8,
          duration: 1500,
          useNativeDriver: true,
          easing: Easing.inOut(Easing.ease),
        }),
        Animated.timing(bounceAnim, {
          toValue: 0,
          duration: 1500,
          useNativeDriver: true,
          easing: Easing.inOut(Easing.ease),
        }),
      ])
    );
    bounce.start();
    return () => bounce.stop();
  }, []);

  return bounceAnim;
};

// Rain drop animation component
function RainDrops({ count = 12 }: { count?: number }) {
  const drops = useRef(
    Array.from({ length: count }, () => ({
      left: Math.random() * 100,
      delay: Math.random() * 2000,
      duration: 1500 + Math.random() * 1000,
      anim: new Animated.Value(0),
    }))
  ).current;

  useEffect(() => {
    drops.forEach((drop) => {
      const animate = () => {
        drop.anim.setValue(0);
        Animated.timing(drop.anim, {
          toValue: 1,
          duration: drop.duration,
          delay: drop.delay,
          useNativeDriver: true,
          easing: Easing.linear,
        }).start(() => animate());
      };
      animate();
    });
  }, []);

  return (
    <Box
      position="absolute"
      top={0}
      left={0}
      right={0}
      bottom={0}
      overflow="hidden"
    >
      {drops.map((drop, i) => (
        <Animated.View
          key={i}
          style={[
            styles.rainDrop,
            {
              left: `${drop.left}%`,
              opacity: drop.anim.interpolate({
                inputRange: [0, 0.1, 0.9, 1],
                outputRange: [0, 0.7, 0.7, 0],
              }),
              transform: [
                {
                  translateY: drop.anim.interpolate({
                    inputRange: [0, 1],
                    outputRange: [0, 150],
                  }),
                },
              ],
            },
          ]}
        >
          <Ionicons name="water" size={20} color="#6BB3D9" />
        </Animated.View>
      ))}
    </Box>
  );
}

export default function WeatherScreen() {
  const [forecasts, setForecasts] = useState<WeatherForecast[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const segments = useSegments() as string[];
  const inStack = segments.includes("(stack)");

  const headerAnim = useFadeIn(0);
  const mainWeatherAnim = useFadeIn(200);
  const detailsAnim = useFadeIn(400);
  const forecastAnim = useFadeIn(600);
  const bounceAnim = useBouncingIcon();

  const fetchWeatherData = useCallback(async () => {
    try {
      setError(null);
      const response = await fetch(
        `${API_BASE_URL}/api/weather/forecast/latest?latitude=13.657096&longitude=123.224535&days=7`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: WeatherForecast[] = await response.json();
      setForecasts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch weather");
      console.error("Weather fetch error:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchWeatherData();
  }, [fetchWeatherData]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchWeatherData();
  }, [fetchWeatherData]);

  const currentWeather = forecasts[0];
  const isRainy =
    currentWeather?.weather.toLowerCase().includes("rain") ||
    currentWeather?.weather.toLowerCase().includes("shower");

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });
  };

  const parseTemp = (tempStr: string) => {
    return parseFloat(tempStr.replace(" °C", ""));
  };

  if (loading) {
    return (
      <Box
        flex={1}
        justifyContent="center"
        alignItems="center"
        bg={THEME.background}
      >
        <VStack alignItems="center" space="md">
          <Spinner size="large" color={THEME.primary} />
          <Text color={THEME.text} fontSize="$lg">
            Loading Weather...
          </Text>
        </VStack>
      </Box>
    );
  }

  if (error) {
    return (
      <Box
        flex={1}
        justifyContent="center"
        alignItems="center"
        bg={THEME.background}
      >
        <VStack alignItems="center" space="md" p="$6">
          <Ionicons name="cloud-offline" size={64} color={THEME.primary} />
          <Text color={THEME.text} fontSize="$lg" textAlign="center">
            {error}
          </Text>
          <Pressable
            onPress={fetchWeatherData}
            bg={THEME.primary}
            px="$6"
            py="$3"
            rounded="$full"
          >
            <Text color="$white" fontWeight="$bold">
              Retry
            </Text>
          </Pressable>
        </VStack>
      </Box>
    );
  }

  return (
    <SafeAreaView
      style={{ flex: 1, backgroundColor: THEME.background }}
      edges={["top"]}
    >
      <ScrollView
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={THEME.primary}
          />
        }
        contentContainerStyle={{ paddingBottom: 30 }}
        style={{ backgroundColor: THEME.background }}
      >
        {/* Back Button (only when opened from stack) */}
        {inStack && (
          <Pressable onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="chevron-back" size={24} color={THEME.primary} />
            <Text color={THEME.primary} fontSize="$md" fontWeight="$medium">
              Back
            </Text>
          </Pressable>
        )}

        {/* Location Header */}
        <Animated.View
          style={{
            opacity: headerAnim.fadeAnim,
            transform: [{ translateY: headerAnim.slideAnim }],
          }}
        >
          <VStack alignItems="center" mt="$2" space="xs">
            <Text fontSize={28} fontWeight="$bold" color={THEME.text}>
              Naga City
            </Text>
            {currentWeather && (
              <Text fontSize="$sm" color={THEME.textLight}>
                {formatDate(currentWeather.datetime)}
              </Text>
            )}
          </VStack>
        </Animated.View>

        {/* Main Weather Display */}
        {currentWeather && (
          <Animated.View
            style={{
              opacity: mainWeatherAnim.fadeAnim,
              transform: [{ translateY: mainWeatherAnim.slideAnim }],
            }}
          >
            <Box style={styles.mainWeatherContainer}>
              {/* Large cloud in back; text in front */}
              <Box style={[styles.heroWrap, { position: "relative" }]}>
                <Animated.View
                  style={[
                    styles.heroIconWrap,
                    styles.iconContainer,
                    { transform: [{ translateY: bounceAnim }] },
                  ]}
                >
                  <Image
                    source={getWeather3DIcon(currentWeather.weather)}
                    style={[
                      styles.heroIcon3D,
                      {
                        zIndex: 0,
                        opacity: 0.6,
                        top: 20,
                        left: 30,
                        position: "absolute",
                      },
                    ]}
                  />
                </Animated.View>

                <Box
                  style={[
                    styles.heroTextWrap,
                    { zIndex: 2, top: 80, right: 90, position: "absolute" },
                  ]}
                >
                  <Text style={styles.heroTemp}>
                    {Math.round(parseTemp(currentWeather.temperature_c))}°C
                  </Text>
                  <Text style={styles.heroCondition}>
                    {currentWeather.weather}
                  </Text>
                </Box>
              </Box>
            </Box>
          </Animated.View>
        )}

        {/* 7-Day Forecast */}
        <Animated.View
          style={{
            opacity: forecastAnim.fadeAnim,
            transform: [{ translateY: forecastAnim.slideAnim }],
          }}
        >
          <Box mx="$4" mt="$6">
            <Text style={styles.sectionTitle}>7-day Forecast</Text>

            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <HStack space="sm" px="$1" py="$2">
                {forecasts.map((forecast, index) => {
                  const temp = parseTemp(forecast.temperature_c);
                  const isToday = index === 0;
                  const dayIcon = getWeather2DIcon(forecast.weather);

                  return (
                    <Box
                      key={index}
                      style={[styles.dayCard, isToday && styles.dayCardActive]}
                    >
                      <Box
                        style={[
                          styles.dayLabel,
                          isToday && styles.dayLabelActive,
                        ]}
                      >
                        <Text
                          color={isToday ? "$white" : THEME.textLight}
                          fontSize="$xs"
                          fontWeight="$bold"
                        >
                          {isToday
                            ? "TODAY"
                            : forecast.weekdate.slice(0, 3).toUpperCase()}
                        </Text>
                      </Box>

                      <Text
                        color={THEME.primary}
                        fontSize="$xl"
                        fontWeight="$bold"
                        mt="$3"
                      >
                        {Math.round(temp)}°C
                      </Text>

                      <Ionicons
                        name={dayIcon.name}
                        size={30}
                        color={dayIcon.color}
                        style={
                          isToday ? styles.dayIcon2DActive : styles.dayIcon2D
                        }
                      />
                    </Box>
                  );
                })}
              </HStack>
            </ScrollView>
          </Box>
        </Animated.View>

        {/* Weather Details */}
        {currentWeather && (
          <Animated.View
            style={{
              opacity: detailsAnim.fadeAnim,
              transform: [{ translateY: detailsAnim.slideAnim }],
            }}
          >
            <Box mx="$4" mt="$6">
              <Text style={styles.sectionTitle}>Weather Details</Text>

              <Box style={styles.detailsCard}>
                <HStack justifyContent="space-between" flexWrap="wrap">
                  <WeatherDetailItem
                    iconName="navigate-outline"
                    label="Wind"
                    value={currentWeather.wind_speed_kmh}
                    subvalue={currentWeather.wind_direction}
                  />
                  <WeatherDetailItem
                    iconName="rainy-outline"
                    label="Rainfall"
                    value={currentWeather.rainfall_mm}
                  />
                  <WeatherDetailItem
                    iconName="speedometer-outline"
                    label="Pressure"
                    value={currentWeather.pressure_pa}
                  />
                  <WeatherDetailItem
                    iconName="water-outline"
                    label="Dewpoint"
                    value={currentWeather.dewpoint_c}
                  />
                </HStack>
              </Box>
            </Box>
          </Animated.View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

function WeatherDetailItem({
  iconName,
  label,
  value,
  subvalue,
}: {
  iconName: React.ComponentProps<typeof Ionicons>["name"];
  label: string;
  value: string;
  subvalue?: string;
}) {
  return (
    <VStack style={styles.detailItem} space="xs">
      <Box style={styles.detailIconCircle}>
        <Ionicons name={iconName} size={20} color={THEME.primary} />
      </Box>
      <Text color={THEME.textLight} fontSize="$xs">
        {label}
      </Text>
      <Text color={THEME.text} fontSize="$md" fontWeight="$bold">
        {value}
      </Text>
      {subvalue ? (
        <Text color={THEME.textLight} fontSize="$xs">
          {subvalue}
        </Text>
      ) : null}
    </VStack>
  );
}

const styles = StyleSheet.create({
  backButton: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  mainWeatherContainer: {
    paddingVertical: 8,
    marginHorizontal: 16,
    position: "relative",
    minHeight: 240,
  },
  heroWrap: {
    position: "relative",
    height: 240,
    justifyContent: "center",
  },
  heroIconWrap: {
    position: "absolute",
    left: -10,
    top: 10,
    zIndex: 1,
  },
  heroIcon3D: {
    width: 230,
    height: 230,
    resizeMode: "contain",
  },
  heroTextWrap: {
    position: "absolute",
    right: 0,
    top: 75,
    zIndex: 3,
    alignItems: "flex-end",
  },
  heroTemp: {
    fontSize: 56,
    fontWeight: "700",
    color: "#1A1A1A",
    lineHeight: 60,
  },
  heroCondition: {
    fontSize: 18,
    color: "#999999",
    marginTop: 4,
  },
  iconContainer: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.18,
    shadowRadius: 18,
    elevation: 12,
  },
  rainDrop: {
    position: "absolute",
    top: 120,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: "#1A1A1A",
    marginBottom: 12,
  },
  detailsCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 20,
    padding: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 3,
  },
  detailItem: {
    width: "48%",
    paddingVertical: 10,
    alignItems: "center",
  },
  detailIconCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: THEME.primaryLight,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 4,
  },
  dayCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    paddingHorizontal: 16,
    paddingVertical: 12,
    alignItems: "center",
    minWidth: 70,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.1,
    shadowRadius: 14,
    elevation: 8,
    marginVertical: 6,
    marginHorizontal: 2,
  },
  dayCardActive: {
    borderWidth: 2,
    borderColor: THEME.primary,
    transform: [{ translateY: -2 }],
  },
  dayLabel: {
    backgroundColor: "#F0F0F0",
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  dayLabelActive: {
    backgroundColor: THEME.primary,
  },
  dayIcon2DActive: {
    marginTop: 10,
    color: THEME.primary,
  },
  dayIcon2D: {
    marginTop: 10,
    color: "#999999",
  },
});
