import { create } from 'zustand';

interface HelpState {
  isHelpOpen: boolean;
  currentHelpPage: string | null;
  openHelp: (pageKey: string) => void;
  closeHelp: () => void;
}

export const useHelpStore = create<HelpState>((set) => ({
  isHelpOpen: false,
  currentHelpPage: null,
  openHelp: (pageKey: string) => set({ isHelpOpen: true, currentHelpPage: pageKey }),
  closeHelp: () => set({ isHelpOpen: false, currentHelpPage: null }),
}));
