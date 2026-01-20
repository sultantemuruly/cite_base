import { create } from "zustand";

interface DocState {
  id: number;
  setId: (id: number) => void;
  title: string;
  setTitle: (title: string) => void;
  chunk_ids: number[];
  setChunkIds: (chunk_ids: number[]) => void;
  chunk_count: number;
  setChunkCount: (chunk_count: number) => void;
}

export const useDocs = create<DocState>()((set) => ({
  id: 0,
  setId: (id: number) => set({ id }),
  title: "",
  setTitle: (title: string) => set({ title }),
  chunk_ids: [],
  setChunkIds: (chunk_ids: number[]) => set({ chunk_ids }),
  chunk_count: 0,
  setChunkCount: (chunk_count: number) => set({ chunk_count }),
}));
