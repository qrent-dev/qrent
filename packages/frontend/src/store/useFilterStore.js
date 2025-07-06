import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

// Create a store for filter management
export const useFilterStore = create()(
  persist(
    (set, get) => ({
      filter: {
        university: 'UNSW',
        priceMin: 'Any',
        priceMax: 'Any',
        commuteTimeMin: 'Any',
        commuteTimeMax: 'Any',
        bedroomMin: 'Any',
        bedroomMax: 'Any',
        bathroomMin: 'Any',
        bathroomMax: 'Any',
        propertyType: 'Any',
        area: [],
        rate: 13,
        avaliableDate: 'Any',
        page: 1,
        page_size: 10,
        newToday: false, // new filter, for merging justlanded and efficiency filter page together
        myFav: false,
        subscriptions: [],
      },
      updateFilter: newFilter => {
        set({ filter: { ...get().filter, ...newFilter } });
      },
    }),
    {
      name: 'filter-progress', // Unique name for the filter state storage
      storage: createJSONStorage(() => localStorage), // Using sessionStorage for persistence
    }
  )
);
