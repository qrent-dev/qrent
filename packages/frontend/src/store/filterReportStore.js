import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

// Create a store for filter management
export const filterReportStore = create()(
  persist(
    (set, get) => ({
      report: {
        currentListings: 0,
        totalListings: 0,
        avgRent: 0,
        avgTravelTime: 0,
        topregions: [],
      },
      updateReport: newReport => {
        set({ report: { ...get().report, ...newReport } });
      },
    }),
    {
      name: 'filter-report',
      storage: createJSONStorage(() => localStorage),
    }
  )
);
