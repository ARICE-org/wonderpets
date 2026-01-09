import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
//import { useColorScheme } from "@/hooks/useColorScheme";

export default function TabsLayout() {
  // const colorScheme = useColorScheme();

  return (
    <Tabs
      screenOptions={{
        headerShown: false, // 🚫 no header = no space
        tabBarActiveTintColor: "#000",
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Home",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="home-outline" size={size} color={color} />
          ),
        }}
      />

      <Tabs.Screen
        name="profile"
        options={{
          title: "Profile",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="person-outline" size={size} color={color} />
          ),
        }}
      />

      {/* 🚫 HIDDEN STACK */}
      <Tabs.Screen
        name="(stack)"
        options={{
          href: null,
        }}
      />
    </Tabs>
  );
}
