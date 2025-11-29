// data/soilData.ts

// Define the structure for a single soil metric object
export interface SoilMetric {
  id: string;
  label: string;
  value: string;
  unit: string;
  status: "good" | "warning" | "bad"; // Restricted status values
  color: string;
}

// Apply the interface to the data array
export const soilMetrics: SoilMetric[] = [
  {
    id: "n",
    label: "Nitrogen",
    value: "15",
    unit: "ppm",
    status: "good",
    color: "$green600",
  },
  {
    id: "k",
    label: "Potassium",
    value: "120",
    unit: "ppm",
    status: "good",
    color: "$green600",
  },
  {
    id: "p",
    label: "Phosphorus",
    value: "49",
    unit: "ppm",
    status: "warning",
    color: "$orange600",
  },
  {
    id: "ph",
    label: "soil Acidity",
    value: "3",
    unit: "pH",
    status: "bad",
    color: "$red600",
  },
];

export default soilMetrics;
