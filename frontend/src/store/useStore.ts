import { create } from 'zustand';

interface AppState {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  // Add other global state here
}

export const useStore = create<AppState>((set) => ({
  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
}));
