import React from "react";
import { HStack } from "@gluestack-ui/themed";
import { SoilMetric } from "../../../Data/soildata";
import SoilItem from "./metricItem";

type MetricRowProps = {
  metrics: SoilMetric[];
};

const MetricRow = ({ metrics }: MetricRowProps) => (
  <HStack flexWrap="wrap" justifyContent="space-between" alignItems="flex-end" width="100%">
    {metrics.map((metric) => (
      <SoilItem
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
