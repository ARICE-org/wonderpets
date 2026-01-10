import type { WeeklyForecastData } from '../../../../lib/api/services/soil-forecast.types';

export interface SoilMetric {
  id: string;
  label: string;
  value: string;
  unit: string;
  status: 'good' | 'warning' | 'bad';
  color: string;
}

export const fallbackSoilMetrics: SoilMetric[] = [
  { id: 'n', label: 'Nitrogen', value: '15', unit: 'ppm', status: 'good', color: '$green600' },
  { id: 'p', label: 'Phosphorus', value: '49', unit: 'ppm', status: 'warning', color: '$orange600' },
  { id: 'k', label: 'Potassium', value: '120', unit: 'ppm', status: 'good', color: '$green600' },
  { id: 'ph', label: 'Soil Acidity', value: '5.8', unit: 'pH', status: 'warning', color: '$orange600' },
];

function scoreToStatus(score: number) {
  if (score >= 80) return 'good' as const;
  if (score >= 60) return 'warning' as const;
  return 'bad' as const;
}

function statusToColor(status: SoilMetric['status']) {
  switch (status) {
    case 'good':
      return '$green600';
    case 'warning':
      return '$orange600';
    case 'bad':
      return '$red600';
  }
}

export function transformForecastToMetrics(w: WeeklyForecastData): SoilMetric[] {
  const metrics: SoilMetric[] = [
    {
      id: 'n',
      label: 'Nitrogen',
      value: String(w.nitrogenPpm ?? 0),
      unit: 'ppm',
      status: w.nitrogenStatus ?? 'good',
      color: statusToColor(w.nitrogenStatus ?? 'good'),
    },
    {
      id: 'p',
      label: 'Phosphorus',
      value: String(w.phosphorusPpm ?? 0),
      unit: 'ppm',
      status: w.phosphorusStatus ?? 'good',
      color: statusToColor(w.phosphorusStatus ?? 'good'),
    },
    {
      id: 'k',
      label: 'Potassium',
      value: String(w.potassiumMeq ?? 0),
      unit: 'meq',
      status: w.potassiumStatus ?? 'good',
      color: statusToColor(w.potassiumStatus ?? 'good'),
    },
    {
      id: 'ph',
      label: 'Soil Acidity',
      value: String(w.pH ?? 0),
      unit: 'pH',
      status: w.phStatus ?? 'good',
      color: statusToColor(w.phStatus ?? 'good'),
    },
  ];
  return metrics;
}

export default fallbackSoilMetrics;
