import React from "react";
import { Box } from "@gluestack-ui/themed";

// Get all props supported by Box
type BoxType = React.ComponentProps<typeof Box>;

interface BaseCardProps extends BoxType {
    children: React.ReactNode;
}

export default function BaseCard({ children, ...rest }: BaseCardProps) {
    return (
        <Box
            bg="$coolGray100"
            rounded="$xl"
            p="$4"
            shadowColor="black"
            shadowOpacity={0.05}
            shadowRadius={8}
            shadowOffset={{ width: 0, height: 2 }}
            {...rest}   // allows width, alignItems, etc.
        >
            {children}
        </Box>
    );
}
