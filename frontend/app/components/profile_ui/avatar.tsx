// components/ProfileAvatar.tsx
import React from "react";
import { View } from "react-native";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

export default function ProfileAvatar({
    source,
    fallback = "??",
    size = 500
}: {
    source?: string; // <--- accepts URL or require()
    fallback?: string;
    size?: number;
}) {
    return (
        <View style={{ alignItems: "center" }}>
            <Avatar style={{ width: size, height: size, borderRadius: size / 2 }}>
                {source ? (
                    <AvatarImage resource={source} /> // <- IMPORTANT: use "source"
                ) : (
                    <AvatarFallback>{fallback}</AvatarFallback>
                )}
            </Avatar>
        </View>
    );
}
