/**
 * Soil Context
 * Manages soil data state including whether user has soil data and navigation triggers
 */
import React, { createContext, useContext, useState, useCallback } from 'react';

interface SoilContextType {
  /** Whether the user has existing soil data */
  hasSoilData: boolean;
  /** Set whether user has soil data */
  setHasSoilData: (value: boolean) => void;
  /** Trigger to open soil dropdown on profile screen */
  shouldOpenSensorDropdown: boolean;
  /** Request to open sensor dropdown (will be consumed by Profile screen) */
  requestOpenSensorDropdown: () => void;
  /** Clear the dropdown open request after consuming */
  clearDropdownRequest: () => void;
  /** Currently selected sensor ID for data upload */
  selectedSensorId: string | null;
  /** Set the selected sensor ID */
  setSelectedSensorId: (id: string | null) => void;
  /** Refetch trigger for soil summary */
  refreshKey: number;
  /** Trigger a refresh of soil data */
  triggerRefresh: () => void;
}

const SoilContext = createContext<SoilContextType | undefined>(undefined);

export function SoilProvider({ children }: { children: React.ReactNode }) {
  const [hasSoilData, setHasSoilData] = useState(false);
  const [shouldOpenSensorDropdown, setShouldOpenSensorDropdown] = useState(false);
  const [selectedSensorId, setSelectedSensorId] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const requestOpenSensorDropdown = useCallback(() => {
    setShouldOpenSensorDropdown(true);
  }, []);

  const clearDropdownRequest = useCallback(() => {
    setShouldOpenSensorDropdown(false);
  }, []);

  const triggerRefresh = useCallback(() => {
    setRefreshKey((prev) => prev + 1);
  }, []);

  return (
    <SoilContext.Provider
      value={{
        hasSoilData,
        setHasSoilData,
        shouldOpenSensorDropdown,
        requestOpenSensorDropdown,
        clearDropdownRequest,
        selectedSensorId,
        setSelectedSensorId,
        refreshKey,
        triggerRefresh,
      }}
    >
      {children}
    </SoilContext.Provider>
  );
}

export function useSoil() {
  const context = useContext(SoilContext);
  if (!context) {
    throw new Error('useSoil must be used inside SoilProvider');
  }
  return context;
}
