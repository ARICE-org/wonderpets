import React from "react";
import { Box, Text } from "@gluestack-ui/themed";

// Get all props supported by Box
type BoxType = React.ComponentProps<typeof Box>;

interface BaseCardProps extends BoxType {
  children: React.ReactNode;
}

export default function BaseCard({ children, ...rest }: BaseCardProps) {
  // Ensure primitive text children are wrapped in a Text component so
  // React Native doesn't throw "Text strings must be rendered within a <Text> component.".
  const normalizedChildren = React.Children.map(children as any, (child) => {
    if (typeof child === "string" || typeof child === "number") {
      return <Text>{child}</Text>;
    }
    return child;
  });

  return (
    <Box
      bg="$coolGray100"
      rounded="$xl"
      p="$4"
      shadowColor="black"
      shadowOpacity={0.05}
      shadowRadius={8}
      shadowOffset={{ width: 0, height: 2 }}
      {...rest} // allows width, alignItems, etc.
    >
      {normalizedChildren}
    </Box>
  );
}
