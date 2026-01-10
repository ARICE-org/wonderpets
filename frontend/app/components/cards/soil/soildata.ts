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
  { id: 'ph', label: 'soil Acidity', value: '5.8', unit: 'pH', status: 'warning', color: '$orange600' },
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
      status: scoreToStatus(w.healthScore),
      color: statusToColor(scoreToStatus(w.healthScore)),
    },
    {
      id: 'p',
      label: 'Phosphorus',
      value: String(w.phosphorusPpm ?? 0),
      unit: 'ppm',
      status: scoreToStatus(w.healthScore),
      color: statusToColor(scoreToStatus(w.healthScore)),
    },
    {
      id: 'k',
      label: 'Potassium',
      value: String(w.potassiumMeq ?? 0),
      unit: 'meq',
      status: scoreToStatus(w.healthScore),
      color: statusToColor(scoreToStatus(w.healthScore)),
    },
    {
      id: 'ph',
      label: 'soil Acidity',
      value: String(w.pH ?? 0),
      unit: 'pH',
      status: w.pH >= 6 && w.pH <= 7.5 ? 'good' : scoreToStatus(w.healthScore),
      color: statusToColor(w.pH >= 6 && w.pH <= 7.5 ? 'good' : scoreToStatus(w.healthScore)),
    },
  ];
  return metrics;
}

export default fallbackSoilMetrics;
