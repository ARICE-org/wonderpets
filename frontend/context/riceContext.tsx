import React, { createContext, useContext, useState } from "react";

interface RiceItem {
  id: string;
  name: string;
  planted: boolean;
  stage?: "Vegetative" | "Flowering" | "Ripening";
  progress?: number;
}

interface RiceContextType {
  riceList: RiceItem[];
  markAsPlanted: (id: string) => void;
}

const RiceContext = createContext<RiceContextType | undefined>(undefined);

export const RiceProvider = ({ children }: { children: React.ReactNode }) => {
  const [riceList, setRiceList] = useState<RiceItem[]>([
    { id: "1", name: "RC 222 Rice", planted: false },
    { id: "2", name: "RC 160 Rice", planted: false },
    { id: "3", name: "RC 480 Rice", planted: false },
    { id: "4", name: "Jasmine Rice", planted: false },
  ]);

  const markAsPlanted = (id: string) => {
    setRiceList((prev) =>
      prev.map((rice) =>
        rice.id === id
          ? {
              ...rice,
              planted: true,
              stage: "Ripening",
              progress: 35,
            }
          : rice
      )
    );
  };

  return (
    <RiceContext.Provider value={{ riceList, markAsPlanted }}>
      {children}
    </RiceContext.Provider>
  );
};

export const useRice = () => {
  const context = useContext(RiceContext);
  if (!context) {
    throw new Error("useRice must be used inside RiceProvider");
  }
  return context;
};
