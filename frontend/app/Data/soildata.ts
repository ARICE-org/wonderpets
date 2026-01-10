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
    label: "Soil Acidity",
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

export const pastYieldData = {
  labels: ["1st Sem", "2nd Sem", "3rd Sem", "4th Sem"],
  datasets: [
    {
      label: "2022 Yield",
      color: "#2568CC",
      data: [20, 45, 60, 40],
    },
    {
      label: "2023 Yield",
      color: "#F434CC",
      data: [30, 55, 50, 65],
    },
    {
      label: "2024 Yield",
      color: "#F5A623",
      data: [40, 60, 55, 70],
    },
    {
      label: "2025 Yield",
      color: "#C2C332",
      data: [44, 20, 76, 90],
    },
  ],
};

export const soilDataByYear = {
  "2023": {
    labels: ["Jan", "Feb", "Mar", "Apr", "May"],
    datasets: [
      { label: "Nitrogen", color: "#34E0A1", data: [12, 15, 13, 14, 16] },
      { label: "Phosphorus", color: "#FF4D4D", data: [8, 9, 7, 10, 9] },
      { label: "Potassium", color: "#4D79FF", data: [20, 18, 19, 21, 20] },
    ],
  },
  "2022": {
    labels: ["Jan", "Feb", "Mar", "Apr", "May"],
    datasets: [
      { label: "Nitrogen", color: "#34E0A1", data: [10, 12, 14, 11, 13] },
      { label: "Phosphorus", color: "#FF4D4D", data: [6, 8, 7, 9, 8] },
      { label: "Potassium", color: "#4D79FF", data: [18, 19, 20, 17, 21] },
    ],
  },
  "2021": {
    labels: ["Jan", "Feb", "Mar", "Apr", "May"],
    datasets: [
      { label: "Nitrogen", color: "#34E0A1", data: [9, 10, 8, 11, 9] },
      { label: "Phosphorus", color: "#FF4D4D", data: [5, 6, 5, 7, 6] },
      { label: "Potassium", color: "#4D79FF", data: [15, 16, 14, 17, 15] },
    ],
  },
};


export const fertilizerValues = [
  { label: "Nitrogen", value: 27, color: "$blue500" },
  { label: "Phosphorus", value: 30, color: "$green500" },
  { label: "Potassium", value: 138, color: "$yellow500" },
];

export default soilMetrics;
