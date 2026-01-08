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

export const data = [
  { label: "Nitrogen", value: "27 ppm", color: "$blue500", symbol: "N" },
  { label: "Phosphorus", value: "30 ppm", color: "$green500", symbol: "P" },
  { label: "Potassium", value: "138 ppm", color: "$yellow500", symbol: "K" },
];
interface Nutrient {
  label: string;
  value: string;
  color: string;
}

export const nutrients: Nutrient[] = [
  { label: "Nitrogen", value: "27 ppm", color: "#4A90E2" },
  { label: "Phosphorus", value: "30 ppm", color: "#50E3C2" },
  { label: "Potassium", value: "138 ppm", color: "#F5A623" },
  { label: "Calcium", value: "1500 ppm", color: "#7ED321" },
];


export default soilMetrics;
