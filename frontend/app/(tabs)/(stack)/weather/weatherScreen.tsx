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
  Platform,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { router, useSegments } from "expo-router";

import {
  getWeatherForecast,
  DailyWeather,
} from "../../../../lib/api/services/weather/weather_forecast";
import { API_BASE_URL } from "../../../../lib/apiBaseUrl";

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

const asLower = (value: unknown) =>
  typeof value === "string" ? value.toLowerCase() : "";

// Get 3D weather icon
const getWeather3DIcon = (weather: string) => {
  switch (asLower(weather)) {
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
  switch (asLower(weather)) {
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
  }, [delay, fadeAnim, slideAnim]);

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
  }, [bounceAnim]);

  return bounceAnim;
};

export default function WeatherScreen() {
  const [forecasts, setForecasts] = useState<DailyWeather[]>([]);
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

  const fetchWeatherData = useCallback(
    async (opts?: { showLoading?: boolean }) => {
      const showLoading = opts?.showLoading ?? false;
      try {
        if (showLoading) setLoading(true);
        setError(null);
        const data = await getWeatherForecast({
          latitude: 13.657096,
          longitude: 123.224535,
          days: 7,
        });
        setForecasts(Array.isArray(data) ? data : []);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to fetch weather";
        setError(message);
        console.error("WeatherScreen fetch error:", { err });
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    []
  );

  useEffect(() => {
    fetchWeatherData({ showLoading: true });
  }, [fetchWeatherData]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchWeatherData();
  }, [fetchWeatherData]);

  const currentWeather = forecasts[0];
  // const isRainy = currentWeatherText.includes("rain") || currentWeatherText.includes("shower"); // unused

  const formatDate = (dateStr: string) => {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });
  };

  const parseTemp = (tempStr: string) => {
    if (!tempStr) return NaN;
    return parseFloat(String(tempStr).replace(" °C", ""));
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
          <Text color={THEME.textLight} fontSize="$xs">
            API: {API_BASE_URL}
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
            onPress={() => {
              void fetchWeatherData({ showLoading: true });
            }}
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
            {!currentWeather && (
              <Text fontSize="$sm" color={THEME.textLight}>
                No forecast data available.
              </Text>
            )}
          </VStack>
        </Animated.View>

        {/* Empty state (prevents “blank white screen” when API returns []) */}
        {!currentWeather && (
          <Box
            mx="$4"
            mt="$6"
            bg={THEME.card}
            borderRadius={16}
            p="$4"
            style={styles.detailsCard}
          >
            <VStack space="xs">
              <Text color={THEME.text} fontSize="$md" fontWeight="$bold">
                No weather data returned
              </Text>
              <Text color={THEME.textLight} fontSize="$sm">
                Check that the backend is running and reachable from your
                device.
              </Text>
              <Text color={THEME.textLight} fontSize="$xs">
                API: {API_BASE_URL}
              </Text>
              <Pressable
                onPress={() => {
                  void fetchWeatherData({ showLoading: true });
                }}
                bg={THEME.primary}
                px="$4"
                py="$2"
                rounded="$full"
                alignSelf="flex-start"
                mt="$2"
              >
                <Text color="$white" fontWeight="$bold">
                  Retry
                </Text>
              </Pressable>
            </VStack>
          </Box>
        )}

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
                    resizeMode="contain"
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
                    {Number.isFinite(parseTemp(currentWeather.temperature_c))
                      ? `${Math.round(
                          parseTemp(currentWeather.temperature_c)
                        )}°C`
                      : "--"}
                  </Text>
                  <Text style={styles.heroCondition}>
                    {currentWeather.weather || "--"}
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
                            : (forecast.weekdate || "---")
                                .slice(0, 3)
                                .toUpperCase()}
                        </Text>
                      </Box>

                      <Text
                        color={THEME.primary}
                        fontSize="$xl"
                        fontWeight="$bold"
                        mt="$3"
                      >
                        {Number.isFinite(temp) ? `${Math.round(temp)}°C` : "--"}
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
    ...(Platform.OS === "web"
      ? { boxShadow: "0px 10px 18px rgba(0, 0, 0, 0.18)" }
      : {
          shadowColor: "#000",
          shadowOffset: { width: 0, height: 10 },
          shadowOpacity: 0.18,
          shadowRadius: 18,
          elevation: 12,
        }),
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
    ...(Platform.OS === "web"
      ? { boxShadow: "0px 2px 8px rgba(0, 0, 0, 0.05)" }
      : {
          shadowColor: "#000",
          shadowOffset: { width: 0, height: 2 },
          shadowOpacity: 0.05,
          shadowRadius: 8,
          elevation: 3,
        }),
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
    ...(Platform.OS === "web"
      ? { boxShadow: "0px 10px 14px rgba(0, 0, 0, 0.10)" }
      : {
          shadowColor: "#000",
          shadowOffset: { width: 0, height: 10 },
          shadowOpacity: 0.1,
          shadowRadius: 14,
          elevation: 8,
        }),
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
