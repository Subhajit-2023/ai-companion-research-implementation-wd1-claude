import { create } from 'zustand';

const useStore = create((set, get) => ({
  characters: [],
  selectedCharacter: null,
  messages: [],
  isLoading: false,
  error: null,
  imageGallery: [],
  sdAvailable: false,

  setCharacters: (characters) => set({ characters }),

  setSelectedCharacter: (character) => set({ selectedCharacter: character, messages: [] }),

  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),

  setMessages: (messages) => set({ messages }),

  appendToLastMessage: (content) => set((state) => {
    const messages = [...state.messages];
    if (messages.length > 0 && messages[messages.length - 1].role === 'assistant') {
      messages[messages.length - 1] = {
        ...messages[messages.length - 1],
        content: messages[messages.length - 1].content + content
      };
    }
    return { messages };
  }),

  setIsLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),

  clearError: () => set({ error: null }),

  setImageGallery: (images) => set({ imageGallery: images }),

  addImageToGallery: (image) => set((state) => ({
    imageGallery: [image, ...state.imageGallery]
  })),

  setSdAvailable: (available) => set({ sdAvailable: available }),

  clearMessages: () => set({ messages: [] }),
}));

export default useStore;
