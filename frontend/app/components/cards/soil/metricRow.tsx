import React from "react";
import { HStack } from "@gluestack-ui/themed";
import { SoilMetric } from "./soildata";
import MetricItem from "./metricItem";

type MetricRowProps = {
  metrics: SoilMetric[];
};

const MetricRow = ({ metrics }: MetricRowProps) => (
  <HStack justifyContent="space-between">
    {metrics.map((metric) => (
      <MetricItem
        key={metric.id}
        label={metric.label}
        value={metric.value}
        unit={metric.unit}
        status={metric.status}
      />
    ))}
  </HStack>
);

export default MetricRow;
