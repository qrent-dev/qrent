import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export const useUserStore = create()(
  persist(
    (set, get) => ({
      userInfo: {
        name: '',
        email: '',
      },
      setUser: userInfo => set({ userInfo: { ...get().userInfo, ...userInfo } }),
    }),
    {
      name: 'user-info', // Name for localStorage
      storage: createJSONStorage(() => localStorage),
    }
  )
);
